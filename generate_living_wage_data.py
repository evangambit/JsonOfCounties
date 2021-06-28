import csv, json, os, re, requests, time, urllib

from bs4 import BeautifulSoup

class Throttler:
  def __init__(self, qps):
    self.waitTime = 1. / qps
    self.lastTime = 0
  def throttle(self):
    time.sleep(max(0, self.waitTime - (time.time() - self.lastTime)))
    self.lastTime = time.time()

throttler = Throttler(qps=0.5)

def fips2url(fips):
	# Shannon County, SD renamed to Oglala Lakota County, SD
	if fips == '46113':
		fips = '46102'
	return f'https://livingwage.mit.edu/counties/{fips}'

with open('base.json', 'r') as f:
	base = json.load(f)

kCacheDir = os.path.join('generated', 'living-wage-cache')
if not os.path.exists(kCacheDir):
	os.mkdir(kCacheDir)

results = {}
for stateName in base:
	for countyName in base[stateName]:
		county = {}

		fips = base[stateName][countyName]['fips']

		cachepath = os.path.join(kCacheDir, fips + '.html')
		if os.path.exists(cachepath):
			with open(cachepath, 'r') as f:
				soup = BeautifulSoup(f.read())
		else:
			url = fips2url(fips)
			throttler.throttle()
			r = requests.get(url)
			assert r.status_code == 200
			soup = BeautifulSoup(r.text)
			with open(cachepath, 'w+') as f:
				f.write(r.text)

		tables = soup.find_all('table')

		assert len(tables) == 3

		wageTable, expenseTable, salaryTable = tables

		C = list(wageTable.children)
		C = [c for c in C if str(c) != '\n']
		assert len(C) == 3
		header = [x for x in C[0].strings if len(x.strip()) > 0]
		assert header == ['1 ADULT', '2 ADULTS', '(1 WORKING)', '2 ADULTS', '(BOTH WORKING)']
		header = [x for x in C[1].strings if len(x.strip()) > 0]
		assert header == ['0\xa0Children', '1\xa0Child', '2\xa0Children', '3\xa0Children', '0\xa0Children', '1\xa0Child', '2\xa0Children', '3\xa0Children', '0\xa0Children', '1\xa0Child', '2\xa0Children', '3\xa0Children']
		C = list(C[2].children)
		C = [c for c in C if str(c) != '\n']
		livingWageRow = [c for c in C[0].children if str(c) != '\n']
		povertyWageRow = [c for c in C[1].children if str(c) != '\n']
		minimumWageRow = [c for c in C[2].children if str(c) != '\n']
		assert livingWageRow[0].text == 'Living Wage'
		assert povertyWageRow[0].text == 'Poverty Wage'
		assert minimumWageRow[0].text == 'Minimum Wage'

		# Living wage computed assuming both adults are working.
		county['livingWage-1-adult'] =  livingWageRow[1].text.strip()
		county['livingWage-2-adults'] =  livingWageRow[9].text.strip()
		county['livingWage-2-adults-2-children'] =  livingWageRow[11].text.strip()

		C = list(expenseTable.children)
		C = [c for c in C if str(c) != '\n']
		assert len(C) == 3
		header = [x for x in C[0].strings if len(x.strip()) > 0]
		assert header == ['1 ADULT', '2 ADULTS', '(1 WORKING)', '2 ADULTS', '(BOTH WORKING)']
		header = [x for x in C[1].strings if len(x.strip()) > 0]
		assert header == ['0\xa0Children', '1\xa0Child', '2\xa0Children', '3\xa0Children', '0\xa0Children', '1\xa0Child', '2\xa0Children', '3\xa0Children', '0\xa0Children', '1\xa0Child', '2\xa0Children', '3\xa0Children']
		C = list(C[2].children)
		C = [c for c in C if str(c) != '\n']
		foodRow = [c for c in C[0].children if str(c) != '\n']
		childCareRow = [c for c in C[1].children if str(c) != '\n']
		medicalRow = [c for c in C[2].children if str(c) != '\n']
		housingRow = [c for c in C[3].children if str(c) != '\n']
		taxesRow = [c for c in C[8].children if str(c) != '\n']
		assert foodRow[0].text == 'Food'
		assert childCareRow[0].text == 'Child Care'
		assert medicalRow[0].text == 'Medical'
		assert housingRow[0].text == 'Housing'
		assert taxesRow[0].text == 'Annual taxes'

		e = {}
		e['food-1-adult'] = foodRow[1].text.strip()
		e['medical-1-adult'] = medicalRow[1].text.strip()
		e['housing-1-adult'] = housingRow[1].text.strip()
		e['taxes-1-adult'] = taxesRow[1].text.strip()
		county['expenses'] = e

		C = list(salaryTable.children)
		C = [c for c in C if str(c) != '\n']
		C = list(C[1].children)
		C = [c for c in C if str(c) != '\n']

		s = {}
		for row in C:
			row = list(row.strings)
			row = [r.strip() for r in row if len(r.strip()) > 0]
			name, income = row
			s[name] = income
		county['salaries'] = s

		results[fips] = county

with open(os.path.join('generated', 'living-wage.json'), 'w+') as f:
	json.dump(results, f, indent=1)


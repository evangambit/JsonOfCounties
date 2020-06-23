"""
Parsers the Washington Post database into JSONs where each
key is a county (e.g. "davidson county, nc") and each value
is a number indicating some quantity (e.g. "number of fatal
police shootigs").

This is tricky because the Washington Post gives cities and
states, but not counties.  We use a website that converts
(city, state) pairs into a county.

We hard-code 72 counties that the website failed to find
matches for.  We also drop various suffixes to try and force
the counties to match the counties in 'all_counties.json'.

Finally, often a city matches to multiple counties.  If
somobody wants to sort through these by hand, they are
welcome to, but there are a *lot* of shootings, and many of
them are very vague on the actual location.  Instead, we
simply distribute a single shooting across multiple counties
(still forcing it to sum up to 1).

The "request-cache.json" file is used to cache requests to
the website, because we want to avoid abusing the University
of Indiana's resources (to the extent we can help it).  As a
result, running this script on your machine should be very
fast (since the entire cache is included in the repository).
"""

import csv, json, os, re, requests, time, urllib

pjoin = os.path.join

from html.parser import HTMLParser

# Removes commas before parsing
def parse_int(x):
	return int(re.sub(r",", "", x))

def pad(t, n, c=' '):
	t = str(t)
	return max(n - len(t), 0) * c + t

class MyHtmlParser(HTMLParser):
  def reset(self):
    super().reset()
    self.depth = 0
    self.trs = []

  def handle_starttag(self, tag, attrs):
  	if tag == 'tr':
  		self.depth += 1
  		self.trs.append([])

  def handle_endtag(self, tag):
  	if tag == 'tr':
  		self.depth -= 1

  def handle_data(self, data):
  	if self.depth > 0:
  		self.trs[-1].append(data)

class Throttler:
  def __init__(self, qps):
    self.waitTime = 1. / qps
    self.lastTime = 0
  def throttle(self):
    time.sleep(max(0, self.waitTime - (time.time() - self.lastTime)))
    self.lastTime = time.time()

# Simple rapper that prevents you from re-making the same request
# twice and throttles you.
class Requester:
	def __init__(self, qps):
		self.throttler = Throttler(qps)
		self.url = 'http://www.stats.indiana.edu/uspr/b/place_query.asp'
		self.kCacheFile = 'request-cache.json'
		# Create new cache if one doesn't exist.
		if not os.path.exists(self.kCacheFile):
			with open(self.kCacheFile, 'w+') as f:
				json.dump({}, f)
		# Load cache.
		with open(self.kCacheFile, 'r') as f:
			self.cache = json.load(f)

	def request(self, state, city):
		cachekey = state + '::' + city
		if cachekey in self.cache:
			return self.cache[cachekey]

		# We wait for a brief period of time to avoid overwhelming
		# their server.
		self.throttler.throttle()

		htmlText = requests.post(self.url, {
			"place_name": city,
			"states": state2id[state]
		}).text
		self.cache[cachekey] = htmlText
		return htmlText

	def save(self):
		with open(self.kCacheFile, 'w+') as f:
			json.dump(self.cache, f, indent=2)

parser = MyHtmlParser()
state2id = {
	"AL": "01",
	"AK": "02",
	"AZ": "04",
	"AR": "05",
	"CA": "06",
	"CO": "08",
	"CT": "09",
	"DE": "10",
	"DC": "11",
	"FL": "12",
	"GA": "13",
	"HI": "15",
	"ID": "16",
	"IL": "17",
	"IN": "18",
	"IA": "19",
	"KS": "20",
	"KY": "21",
	"LA": "22",
	"ME": "23",
	"MD": "24",
	"MA": "25",
	"MI": "26",
	"MN": "27",
	"MS": "28",
	"MO": "29",
	"MT": "30",
	"NE": "31",
	"NV": "32",
	"NH": "33",
	"NJ": "34",
	"NM": "35",
	"NY": "36",
	"NC": "37",
	"ND": "38",
	"OH": "39",
	"OK": "40",
	"OR": "41",
	"PA": "42",
	"RI": "44",
	"SC": "45",
	"SD": "46",
	"TN": "47",
	"TX": "48",
	"UT": "49",
	"VT": "50",
	"VA": "51",
	"WA": "53",
	"WV": "54",
	"WI": "55",
	"WY": "56",
}

requester = Requester(0.5)

def get_county(state, city, cache={}):
	htmlText = requester.request(state, city)

	parser.reset()
	parser.feed(htmlText)
	if len(parser.trs) < 2 or parser.trs[1] == ["No Cities or Towns Found"]:
		# Sometimes the county instead of the city.  In this
		# case we can just return the county directly!
		if city[-7:] == ' County':
			return {
				city + ', ' + state: 1.0
			}
		return None

	# We groups cities by county and distribute the shooting
	# proportinally.
	county_names = [x[2] for x in parser.trs[1:]]
	populations = [parse_int(x[1]) for x in parser.trs[1:]]
	percent_in_county = [float(x[3][:-1]) / 100.0 for x in parser.trs[1:]]

	populations = [a * b for (a, b) in zip(populations, percent_in_county)]

	# Normalize to 1
	s = sum(populations)
	populations = [p / s for p in populations]
	assert abs(sum(populations) - 1.0) < 1e-4, populations

	A = {}
	for pop, name in zip(populations, county_names):
		A[name] = A.get(name, 0) + pop
	county_names = list(A.keys())

	assert abs(sum(A.values()) - 1.0) < 1e-4, populations

	return A


# Load police shootings data.
with open(pjoin('data', 'fatal-police-shootings-data.csv'), 'r') as f:
	reader = csv.reader(f, delimiter=',', quotechar='"')
	rows = [row for row in reader]
header = rows[0]
rows = rows[1:]

rows = [row for row in rows if row[2][:-5] == '2019-']

A = {
	'gun': 0,
	'knife': 0,
	'unarmed': 0,
	'undetermined': 0,
	'vehicle': 0,
	'other': 0,
}
for row in rows:
	if row[4] in A:
		A[row[4]] += 1
	else:
		A['other'] += 1

print(f'{pad(len(rows), 4)} total fatal police shootings')
print(f'{pad(A["unarmed"], 4)} were unarmed')
print(f'{pad(A["gun"], 4)} were armed with a gun')
print(f'{pad(A["undetermined"], 4)} were undetermined')

# For historical reasons we use all-counties.json as the
# groundtruth for this script, and try to warp county names
# to fit them.  As the code exists now this is a little silly
# since we do a similar thing later in create_json.py.
# data/all-counties.json was created by some script (I think
# based on census data) that has since been lost to time.
with open(pjoin('data', 'all-counties.json'), 'r') as f:
	all_counties = json.load(f)

kHardCode = {
	"Whitehaven, TN": "Shelby County, TN",
	"Glen Valley, CA": "Riverside County, CA",
	"Logan Township, NJ": "Gloucester County, NJ",
	"O'Fallon, MO": "St. Charles County, MO",
	"Mercury, NV": "Nye County, NV",
	"Kirkwood, NY": "Broome County, NY",
	"LaSalle, CO": "Weld County, CO",
	"Walter Hill, TN": "Rutherford County, TN",
	"Joilet, IL": "Will County, IL",
	"Napa Valley, CA": "Napa County, CA",
	"Honolulu, HI": "Honolulu County, HI",
	"Pelehatchie, MS": "Rankin County, MS",
	"Walton, WV": "Roane County, WV",
	"Huger, SC": "Berkeley County, SC",
	"Glenoma, WA": "Lewis County, WA",
	"Pennfield Township, MI": "Calhoun County, MI",
	"Salacoa, GA": "Cherokee County, GA",
	"Ernul, NC": "Craven County, NC",
	"LaFollette, TN": "Campbell County, TN",
	"Ahwatukee, AZ": "Maricopa County, AZ",
	"Meadowlake, NM": "Valencia County, NM",
	"Bruce, FL": "Walton County, FL",
	"Hiltons, VA": "Scott County, VA",
	"Tunbridge, VT": "Orange County, VT",
	"Montgomery Creek, KY": "Perry County, KY",
	"Bagley Township, MI": "Otsego County, MI",
	"San Ysidro, CA": "San Diego County, CA",
	"Davidsonville, MD": "Anne Arundel County, MD",
	"Bonnyman, KY": "Perry County, KY",
	"Porteau, OK": "Le Flore County, OK",
	"Friendly Hills, CO": "Jefferson County, CO",
	"Big Sur, CA": "Monterey County, CA",
	"Phoenix, MD": "Baltimore County, MD",
	"Orange, NJ": "Essex County, NJ",
	"Penn Hills, PA": "Allegheny County, PA",
	"Ross Township, PA": "Allegheny County, PA",
	"Boyton Beach, FL": "Palm Beach County, FL",
	"Irvington, NJ": "Essex County, NJ",
	"Shaler Township, PA": "Allegheny County, PA",
	"Formosa, AR": "Van Buren County, AR",
	"Springville, IN": "Lawrence County, IN",
	"Coeur d'Alene, ID": "Kootenai County, ID",
	"Soddy Daisy, TN": "Hamilton County, TN",
	"Cotter, MO": "Pemiscot County, MO",
	"Drennen, WV": "Nicholas County, WV",
	"Ethel, LA": "East Feliciana Parish, LA",
	"Hope Ranch, CA": "Santa Barbara County, CA",
	"Lake Lanier, GA": "Hall County, GA",
	"Ona, WV": "Cabell County, WV",
	"Leon, WI": "Monroe County, WI",
	"Ashtabula Township, OH": "Ashtabula County, OH",
	"Mandarin, FL": "Duval County, FL",
	"Fox Crossing, WI": "Winnebago County, WI",
	"West Kewaunee, WI": "Kewaunee County, WI",
	"Gaines Township, MI": "Kent County, MI",
	"Sparks, MD": "Baltimore County, MD",
	"Hanover Township, PA": "Beaver County, PA",
	"St. Helena Parish, LA": "St. Helena Parish, LA",
	"Semmes, AL": "Mobile County, AL",
	"Arietta, NY": "Hamilton County, NY",
	"Nelson Township, PA": "Tioga County, PA",
	"Redford Township, MI": "Wayne County, MI",
	"Limerick, ME": "York County, ME",
	"Elizabethon, TN": "Carter County, TN",
	"Bracketville, TX": "Kinney County, TX",
	"Jamaica, NY": "Queens County, NY",
	"Treme, LA": "Orleans Parish, LA",

	# I had to Google the specific shootings for these
	# cases.
	"North Escambia, FL": "Escambia County, FL",
	"Sun City, SC": "Beaufort County, SC",
	"Sherman Oaks, CA": "Los Angeles County, CA",


	# Typos!
	"Charlottte, NC": "Mecklenburg County, NC",
	"Watuaga County, NC": "Watauga County, NC",
}

number_of_shootings = {}
number_of_unarmed_shootings = {}
number_of_firearm_shootings = {}

# id,name,date,manner_of_death,armed,age,gender,race,city,state,signs_of_mental_illness,threat_level,flee,body_camera
for row_idx, row in enumerate(rows):
	state = row[header.index('state')]
	city = row[header.index('city')]
	was_unarmed = row[header.index('armed')] == 'unarmed'
	had_firearm = row[header.index('armed')] == 'gun'

	if f'{city}, {state}' in kHardCode:
		counties = {
			kHardCode[f'{city}, {state}']: 1
		}
	else:
		counties = get_county(state, city)

	if counties is None:
		# print(f'{city}, {state}')
		print(row)
		continue

	# Reformt county so that it matches the name in
	# the CDC's dataset.  Shockingly only one county
	# cannot be found (Watuaga County, NC) which seems
	# to be an error by the CDC.
	for key in counties:
		assert key[-4:-2] == ', '
		state = key[-2:].lower()
		county = key[:-4].lower()

		if county[-20:] == ' city (county equiv)':
			county = county[:-20]

		is_valid = [state, county] in all_counties
		if not is_valid:
			if county[-7:] == ' county':
				is_valid |= [state, county[:-7]] in all_counties
			else:
				is_valid |= [state, county + ' county'] in all_counties

		k = f'{county}, {state}'.lower()
		if k not in number_of_shootings:
			number_of_shootings[k] = 0.0
			number_of_unarmed_shootings[k] = 0.0
			number_of_firearm_shootings[k] = 0.0
		number_of_shootings[k] += counties[key]
		if was_unarmed:
			number_of_unarmed_shootings[k] += counties[key]
		if had_firearm:
			number_of_firearm_shootings[k] += counties[key]

	if row_idx % 50 == 0:
		requester.save()

with open(pjoin('generated', 'shootings-by-county.json'), 'w+') as f:
	json.dump(number_of_shootings, f)

with open(pjoin('generated', 'unarmed-shootings-by-county.json'), 'w+') as f:
	json.dump(number_of_unarmed_shootings, f)

with open(pjoin('generated', 'shootings-by-county-where-victim-had-firearm.json'), 'w+') as f:
	json.dump(number_of_firearm_shootings, f)


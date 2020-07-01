import code, copy, csv, json, math, os, re

# pip install pyshp
import shapefile

import matplotlib.pyplot as plt
import numpy as np

import os

pjoin = os.path.join

# pip install Shapely
from shapely import geometry
from shapely.geometry import Point

abbreviation_to_name = {
	"AL": "Alabama",
	"AK": "Alaska",
	"AZ": "Arizona",
	"AR": "Arkansas",
	"CA": "California",
	"CO": "Colorado",
	"CT": "Connecticut",
	"DE": "Delaware",
	"DC": "District of Columbia",
	"FL": "Florida",
	"GA": "Georgia",
	"GU": "Guam",
	"HI": "Hawaii",
	"ID": "Idaho",
	"IL": "Illinois",
	"IN": "Indiana",
	"IA": "Iowa",
	"KS": "Kansas",
	"KY": "Kentucky",
	"LA": "Louisiana",
	"ME": "Maine",
	"MD": "Maryland",
	"MA": "Massachusetts",
	"MI": "Michigan",
	"MN": "Minnesota",
	"MS": "Mississippi",
	"MO": "Missouri",
	"MT": "Montana",
	"NE": "Nebraska",
	"NV": "Nevada",
	"NH": "New Hampshire",
	"NJ": "New Jersey",
	"NM": "New Mexico",
	"NY": "New York",
	"NC": "North Carolina",
	"ND": "North Dakota",
	"OH": "Ohio",
	"OK": "Oklahoma",
	"OR": "Oregon",
	"PA": "Pennsylvania",
	"RI": "Rhode Island",
	"SC": "South Carolina",
	"SD": "South Dakota",
	"TN": "Tennessee",
	"TX": "Texas",
	"UT": "Utah",
	"VT": "Vermont",
	"VI": "Virgin Islands",
	"VA": "Virginia",
	"WA": "Washington",
	"WV": "West Virginia",
	"WI": "Wisconsin",
	"WY": "Wyoming",
}

fips_code_to_name = {
	"01": "Alabama",
	"02": "Alaska",
	"04": "Arizona",
	"05": "Arkansas",
	"06": "California",
	"08": "Colorado",
	"09": "Connecticut",
	"10": "Delaware",
	"11": "District of Columbia",
	"12": "Florida",
	"13": "Georgia",
	"15": "Hawaii",
	"16": "Idaho",
	"17": "Illinois",
	"18": "Indiana",
	"19": "Iowa",
	"20": "Kansas",
	"21": "Kentucky",
	"22": "Louisiana",
	"23": "Maine",
	"24": "Maryland",
	"25": "Massachusetts",
	"26": "Michigan",
	"27": "Minnesota",
	"28": "Mississippi",
	"29": "Missouri",
	"30": "Montana",
	"31": "Nebraska",
	"32": "Nevada",
	"33": "New Hampshire",
	"34": "New Jersey",
	"35": "New Mexico",
	"36": "New York",
	"37": "North Carolina",
	"38": "North Dakota",
	"39": "Ohio",
	"40": "Oklahoma",
	"41": "Oregon",
	"42": "Pennsylvania",
	"44": "Rhode Island",
	"45": "South Carolina",
	"46": "South Dakota",
	"47": "Tennessee",
	"48": "Texas",
	"49": "Utah",
	"50": "Vermont",
	"51": "Virginia",
	"53": "Washington",
	"54": "West Virginia",
	"55": "Wisconsin",
	"56": "Wyoming",
	"60": "American Samoa",
	"66": "Guam",
	"69": "Northern Mariana Islands",
	"72": "Puerto Rico",
	"78": "Virgin Islands",
}

not_states = set([
	"American Samoa",
	"Guam",
	"Northern Mariana Islands",
	"Puerto Rico",
	"Virgin Islands",
])

# Maps formly independent cities to the counties they
# now belong to.  This way we can add the deaths from
# these cities (which the CDC keeps separate, since its
# data goes back to 1999) to the counties the cities
# now belong to.
former_independent_cities_to_counties = {
	"Virginia": {
		"clifton forge city": "alleghany county",
		"bedford city": "bedford county",
	}
}

class CountyNameMerger:
	kHardCoded = {
		"Alabama": {
			"de kalb": "dekalb county",	
		},
		"Alaska": {
			"anchorage borough": "anchorage municipality",
			"juneau borough": "juneau city and borough",
			"petersburg borough/census area": "petersburg borough",
			"sitka borough": "sitka city and borough",
			"skagway-hoonah-angoon census area" : "skagway municipality",
			"wrangell-petersburg census area": "wrangell city and borough",
			"yakutat borough": "yakutat city and borough",
			# Formerly known as Wade Hampton Census Area
			"wade hampton census area": "kusilvak census area",
			# Renamed in 2008
			"prince of wales-outer ketchikan census area": "prince of wales-hyder census area",

			"anchorage borough/municipality": "anchorage municipality",
			"juneau borough/city": "juneau city and borough",
			"sitka borough/city": "sitka city and borough",
			"wrangell borough/city": "wrangell city and borough",
			"yakutat borough/city": "yakutat city and borough",

			"municipality of anchorage": "anchorage municipality",
			"city and borough of juneau": "juneau city and borough",
			"petersburg census area": "petersburg borough",
		},
		"California": {
			"san francisco county/city": "san francisco county",
		},
		"Colorado": {
			"broomfield county/city": "broomfield county",
		},
		"District of Columbia": {
			"washington": "district of columbia",
			"district of columbia county": "district of columbia",
		},
		"Florida": {
			"de soto": "desoto county",
		},
		"Georgia": {
			"de kalb": "dekalb county",
		},
		"Idaho": {
			"fremont (includes yellowstone park)": "fremont county"
		},
		"Illinois": {
			"la salle": "lasalle county",
			"du page": "dupage county",
			"de kalb": "dekalb county",
		},
		"Indiana": {
			"de kalb": "dekalb county",
			"de kalb county": "dekalb county",
			"la porte county": "laporte county",
			"la porte": "laporte county",
			"de kalb": "dekalb county",
			"la grange": "lagrange county",
		},
		"Iowa": {
			"o brien": "o'brien county",
		},
		"Louisiana": {
			"la salle parish": "lasalle parish",
			"la salle": "lasalle parish",
		},
		"Maryland": {
			"baltimore (independent city)": "baltimore city",
			"baltimore city county": "baltimore city",
			"prince georges": "prince george's county",
			"queen annes": "queen anne's county",
			"st. marys": "st. mary's county",
		},
		"Mississippi": {
			"de soto": "desoto county",
		},
		"Missouri": {
			"jackson county (including other portions of kansas city)": "jackson county",
			"city of st. louis": "st. louis city",
			"st. louis city county": "st. louis city",
			"Jackson County (including other portions of Kansas City)": "Jackson County",
			"de kalb": "dekalb county",
		},
		"Nevada": {
			"carson city county": "carson city"
		},
		"New Mexico": {
			"debaca county": "de baca county",
			"dona ana county": "doña ana county",
			"dona ana": "doña ana county",
		},
		"North Dakota": {
			"la moure": "lamoure county",
		},
		"Pennsylvania": {
			"mc kean county": "mckean county",
		},
		"South Dakota": {
			"shannon county": "oglala lakota county",
			"shannon": "oglala lakota county",
		},
		"Tennessee": {
			"de kalb": "dekalb county",	
		},
		"Texas": {
			"de witt": "dewitt county",
		},
		"Virginia": {
			"colonial heights cit": "colonial heights city"
		}
	}


# if county not in states[state] and county + ' county' in states[state]:
# 	county = county + ' county'
# if county not in states[state] and county + ' parish' in states[state]:
# 	county = county + ' parish'
# assert county in states[state], f'{county}, {state}'


	def __init__(self):
		with open('base.json', 'r') as f:
			self.states = json.load(f)

	def merge_state(self, state, list1, list2, allow_missing, missing):
		if (not allow_missing) and len(missing.get(state, {})) == 0:
			assert len(list1) == len(list2), f"{state}\n\n{sorted(list1)}\n\n{sorted(list2)}"
			assert len(set(list1)) == len(list1)
			assert len(set(list2)) == len(list2)

		hardCoded = CountyNameMerger.kHardCoded.get(state, {})

		M = {}

		foo = 'honolulu' in list1

		i = 0
		while i < len(list1):
			county = list1[i]
			if county[:3] == 'st ':
				county = 'st. ' + county[3:]

			if county[-19:] == ' (independent city)':
				if county[-23:-18] != 'city ':
					county = county[:-19] + ' city'
				else:
					county = county[:-19]

			if county[-12:] == ' county/city':
				county = county[:-5]
			if county[-12:] == ' county/town':
				county = county[:-5]

			if county in hardCoded:
				j = list2.index(hardCoded[county])
				M[list1[i]] = list2[j]
				del list1[i]
				del list2[j]
			elif county in list2:
				j = list2.index(county)
				M[list1[i]] = list2[j]
				del list1[i]
				del list2[j]
			elif county + ' county' in list2:
				j = list2.index(county + ' county')
				M[list1[i]] = list2[j]
				del list1[i]
				del list2[j]
			elif state == 'Louisiana' and county + ' parish' in list2:
				j = list2.index(county + ' parish')
				M[list1[i]] = list2[j]
				del list1[i]
				del list2[j]
			else:
				i += 1

		if state not in missing:
			assert len(list1) == 0, f"{state}\n\n{list1}\n\n{list2}"
		else:
			assert len([x for x in list1 if x not in missing[state]]) == 0

		if not allow_missing:
			assert len(list2) - len(missing.get(state, {})) == 0, list2

		# Assert mapping is not many-to-1
		assert len(M.values()) == len(set(M.values()))

		return M

	def merge(self, states, allow_missing=False, missing={}):
		if not allow_missing:
			assert len(states) == 51
		for state in states:
			M = self.merge_state(
				state,
				list(states[state].keys()),
				list(self.states[state].keys()),
				allow_missing=allow_missing,
				missing=missing
			)
			for county in M:
				self.add_to_json(
					self.states[state][M[county]],
					states[state][county]
				)

	def add_to_json(self, base, addition):
		for k in addition:
			assert k not in base
			base[k] = addition[k]

merger = CountyNameMerger()

def get_geometry():
	states = {}

	# https://stackoverflow.com/questions/24467972/calculate-area-of-polygon-given-x-y-coordinates
	def area(x, y):
		return 0.5*np.abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))

	sf = shapefile.Reader(pjoin('data', 'tl_2017_us_county/tl_2017_us_county.shp'))

	# Add geometric data for countries.
	for s in sf:
		state = fips_code_to_name[s.record.STATEFP]
		if state in not_states:
			continue
		if state not in states:
			states[state] = {}
		county_name = s.record.NAMELSAD.lower()
		poly = geometry.Polygon(s.shape.points)
		states[state][county_name] = {
			"area": poly.convex_hull.area,
			"min_location": poly.bounds[:2],
			"max_location": poly.bounds[2:]
		}
		latitude_ish = (states[state][county_name]["min_location"][1] + states[state][county_name]["max_location"][1]) / 2
		states[state][county_name]["area"] *= math.cos(latitude_ish * math.pi / 180)

	return states


merger.merge(get_geometry())

def get_demographics():
	age_code_to_group = {
	  0: "all",
		1: "0-4",
		2: "5-9",
		3: "10-14",
		4: "15-19",
		5: "20-24",
		6: "25-29",
		7: "30-34",
		8: "35-39",
		9: "40-44",
		10: "45-49",
		11: "50-54",
		12: "55-59",
		13: "60-64",
		14: "65-69",
		15: "70-74",
		16: "75-79",
		17: "80-84",
		18: "85+"
	}

	# https://www2.census.gov/programs-surveys/popest/technical-documentation/file-layouts/2010-2018/cc-est2018-alldata.pdf
	year_code_to_year = {
		 "1": "4/1/2010",
		 "2": "4/1/2010", # sic
		 "3": "7/1/2010",
		 "4": "7/1/2011",
		 "5": "7/1/2012",
		 "6": "7/1/2013",
		 "7": "7/1/2014",
		 "8": "7/1/2015",
		 "9": "7/1/2016",
		"10": "7/1/2017",
		"11": "7/1/2018",
	}
	# After downloading this file you should open it with a text editor (
	# I use Sublime) and re-encode it as utf8.

	states = {}

	with open(pjoin('data', 'cc-est2018-alldata.csv'), 'r') as f:
		reader = csv.reader(f, delimiter=',')
		header = next(reader)
		rows = [row for row in reader]
		assert header[:7] == ['SUMLEV', 'STATE', 'COUNTY', 'STNAME', 'CTYNAME', 'YEAR', 'AGEGRP']
		for row in rows:
			state = row[3]
			if state not in states:
				states[state] = {}

			county = row[4].lower()

			# We only grab the latest year available and ignore the
			# other rows.
			if year_code_to_year[row[5]] != '7/1/2018':
				continue

			age_group = int(row[6])
			if age_group == 0:
				# age group "0" is everyone.  We grab racial data from
				# this row.  The racial break down done by the Census
				# Bureau is... intense, with 73 different columns.  To
				# keep the file size reasonable I don't track them all.
				# Fortunately the code and data is freely available so
				# it is trivial for you to add more columns if you like!

				# We assume this is the first row we see.
				assert county not in states[state]
				states[state][county] = {}
				states[state][county]['race_demographics'] = {}
				states[state][county]['age_demographics'] = {}

				states[state][county]['male'] = int(row[8])
				states[state][county]['female'] = int(row[9])

				total = int(row[7])
				states[state][county]['population'] = total

				states[state][county]['race_demographics']['non_hispanic_white_alone_male'] = int(row[34]) / total
				states[state][county]['race_demographics']['non_hispanic_white_alone_female'] = int(row[35]) / total

				states[state][county]['race_demographics']['black_alone_male'] = int(row[12]) / total
				states[state][county]['race_demographics']['black_alone_female'] = int(row[13]) / total

				states[state][county]['race_demographics']['asian_alone_male'] = int(row[16]) / total
				states[state][county]['race_demographics']['asian_alone_female'] = int(row[17]) / total

				states[state][county]['race_demographics']['hispanic_male'] = int(row[56]) / total
				states[state][county]['race_demographics']['hispanic_female'] = int(row[57]) / total

			else:
				states[state][county]['age_demographics'][age_code_to_group[int(row[6])]] = int(row[7]) / states[state][county]['population']

			assert county in states[state]

	for state_name in states:
		for county_name in states[state_name]:
			assert 'race_demographics' in states[state_name][county_name]

	return states

merger.merge(get_demographics())

def get_cdc_deaths():
	states = {}
	for varname, fn in zip(['suicides', 'firearm suicides', 'homicides'], ["Compressed Mortality, 1999-2016 (all suicides).txt", "Compressed Mortality, 1999-2016 (firearm suicides).txt", "Compressed Mortality (assaults), 1999-2016.txt"]):
		with open(pjoin('data', fn), 'r') as f:
			reader = csv.reader(f, delimiter='\t', quotechar='"')
			rows = [row for row in reader]
		header = rows[0]
		rows = rows[1:]
		rows = rows[:rows.index(['---']) - 1]
		former_independent_cities = {}
		for row in rows:
			_, county, _, deaths, _, _ = row
			county = county.lower()
			state = abbreviation_to_name[county.split(', ')[-1].upper()]
			if state not in states:
				states[state] = {}
			county = ', '.join(county.split(', ')[:-1])

			# These counties changed their names recently, and rows with
			# both the old names and new names are found in the CDC
			# dataset, so we simply ignore these names.
			if county in ['prince of wales-outer ketchikan census area', 'skagway-hoonah-angoon census area', "wrangell-petersburg census area"]:
				continue

			if deaths == 'Suppressed':
				deaths = None
			else:
				deaths = int(deaths)

			if state in former_independent_cities_to_counties and county in former_independent_cities_to_counties[state]:
				county = former_independent_cities_to_counties[state][county]
				if state not in former_independent_cities:
					former_independent_cities[state] = {}
				former_independent_cities[state][county] = deaths
				continue

			if county not in states[state]:
				states[state][county] = {
					"deaths": {}
				}
			assert varname not in states[state][county]
			states[state][county]["deaths"][varname] = deaths

		# Add formly independent cities to their respective counties.
		for state in former_independent_cities:
			for county in former_independent_cities[state]:
				# If either value was suppressed, we keep the concatenated
				# value as None.
				if states[state][county]["deaths"][varname] is None:
					continue
				if former_independent_cities[state][county] is None:
					continue
				states[state][county]["deaths"][varname] += former_independent_cities[state][county]

		for state in states:
			for county in states[state]:
				assert varname in states[state][county]["deaths"]

	return states

merger.merge(get_cdc_deaths())

# Labor force data
# https://www.bls.gov/lau/#cntyaa

def get_labor_force():
	states = {}

	with open(pjoin('data', 'laborforce.txt'), 'r') as f:
		lines = f.readlines()
		for line in lines[6:]:
			line = line.strip()
			if len(line) == 0:
				break
			laus_code, state_fips_code, county_fips_code, county_name, year, labor_force, employed, unemployed, unemployment_rate = re.sub(r"  +", "  ", line).split("  ")

			if county_name == "District of Columbia":
				state = "District of Columbia"
				county_name = state.lower()
			else:
				state = county_name.split(', ')[-1]
				if state not in abbreviation_to_name:
					continue
				state = abbreviation_to_name[state]
				county_name = ', '.join(county_name.split(', ')[:-1]).lower()

			if state in not_states:
				continue

			if state not in states:
				states[state] = {}

			county = {}
			county['labor_force'] = float(labor_force.replace(",",""))
			county['employed'] = float(employed.replace(",",""))
			county['unemployed'] = float(unemployed.replace(",",""))
			county['unemployment_rate'] = float(unemployment_rate)
			assert county_name not in states[state]
			states[state][county_name] = county

	# Missing county...
	assert "kalawao county" not in states["Hawaii"]
	states["Hawaii"]["kalawao county"] = {
		"labor_force": None,
		"employed": None,
		"unemployed": None,
		"unemployment_rate": None
	}

	return states

merger.merge(get_labor_force())

def get_fatal_police_shootings():
	states = {}

	for varname, fn in zip(
		['total', 'unarmed', 'fire-armed'],
		['shootings-by-county.json', 'unarmed-shootings-by-county.json', 'shootings-by-county-where-victim-had-firearm.json']):
		with open(pjoin('generated', fn), 'r') as f:
			shootings = json.load(f)

			for k in shootings:
				state_name = abbreviation_to_name[k[-2:].upper()]
				if state_name not in states:
					states[state_name] = {}
				state = states[state_name]
				county_name = k[:-4]

				if county_name not in state:
					state[county_name] = {
						"fatal_police_shootings": {}
					}

				state[county_name]["fatal_police_shootings"][varname] = shootings[k]

	return states

# Fatal police shootings are unique in that we don't have an
# entry for every county, because the Washington Post tracks
# stats by *shooting* rather than by county.  As a result, we
# need to tolerate having missing counties.
merger.merge(get_fatal_police_shootings(), allow_missing=True)

# After we merge, add zeros for all missing counties (which
# aren't present in the Washington Post dataset, simply because
# they had no fatal police shootings).
for state in merger.states:
	for county in merger.states[state]:
		if "fatal_police_shootings" not in merger.states[state][county]:
			merger.states[state][county]["fatal_police_shootings"] = {}

		if "total" not in merger.states[state][county]["fatal_police_shootings"]:
			merger.states[state][county]["fatal_police_shootings"]["total"] = 0
		if "unarmed" not in merger.states[state][county]["fatal_police_shootings"]:
			merger.states[state][county]["fatal_police_shootings"]["unarmed"] = 0
		if "fire-armed" not in merger.states[state][county]["fatal_police_shootings"]:
			merger.states[state][county]["fatal_police_shootings"]["fire-armed"] = 0

def get_avg_income():
	states = {}
	for fn in os.listdir(pjoin('data', 'CAINC1')):
		with open(pjoin('data', 'CAINC1', fn), 'r', encoding='Latin-1') as f:
			reader = csv.reader(f, delimiter=',')
			header = next(reader)
			rows = [row for row in reader]
			for row in rows[3:-1]:
				if len(row) < 7:
					continue

				if row[6] != 'Per capita personal income (dollars) 2/':
					continue

				# This is an effective way to ensure the row is
				# sensible (and not a footer / footnote).
				try:
					avg_income = int(row[-1])
				except ValueError:
					continue

				loc = row[1]
				# ignore fotenotes...
				while loc[-1] == '*':
					loc = loc[:-1]
				assert loc[-4:-2] == ', '
				county = loc[:-4].lower()
				state = abbreviation_to_name[loc[-2:]]

				if state not in states:
					states[state] = {}

				# These counties are combined...
				if loc == 'Maui + Kalawao, HI':
					assert "maui county" not in states[state]
					assert "kalawao county" not in states[state]
					states[state]['maui county'] = {
						"avg_income": avg_income
					}
					states[state]['kalawao county'] = {
						"avg_income": avg_income
					}
					continue

				# Independent cities are merged with their surrounding counties.
				# We un-merge them here.
				if '+' in county:
					parts = [x.strip() for x in re.findall(r"[^,\+]+", county)]
					assert parts[0] + ' county' not in states[state]
					states[state][parts[0] + ' county'] = {
						"avg_income": avg_income
					}
					for part in parts[1:]:
						if part[-5:] != ' city':
							part += ' city'
						assert part not in states[state]
						states[state][part] = {}
						states[state][part]['avg_income'] = avg_income
					continue

				assert county not in states[state]
				states[state][county] = {
					"avg_income": avg_income
				}

	for state in states:
		for county in states[state]:
			assert 'avg_income' in states[state][county]

	return states

merger.merge(get_avg_income())

def get_covid():
	blacklist = {
		"Alaska": {
			# Ordinarily we'd map this to "kusilvak census area" but,
			# (I assume due to an oversight by either the CDC or
			# usafacts.org) this county represented twice (once for
			# each name).  Fortunately both death counts are zero, so
			# we just ignore it for now.
			"wade hampton census area": None,
		},
		"California": {
			"grand princess cruise ship": None,
		},
	}

	states = {}

	new_york_unallocated = 0

	for varname, fn in zip(['deaths', 'confirmed'], ['covid_deaths_usafacts.csv', 'covid_confirmed_usafacts.csv']):
		with open(pjoin('data', fn), 'r') as f:
			reader = csv.reader(f, delimiter=',')
			header = next(reader)
			for row in reader:
				if row[1] == 'Statewide Unallocated':
					continue
				county = row[1].lower()
				state = abbreviation_to_name[row[2]]

				if state not in states:
					states[state] = {}

				# Lacking any clear/easy alternatives, we simply dump
				# these in New York County at the end of the loop.
				# We assert that the number of unallocated deaths is
				# pretty small.  If it ever becomes large (relative
				# to the New York counties) we may want to revisit
				# our approach.
				if county == "new york city unallocated/probable":
					new_york_unallocated = int(row[-1])
					assert new_york_unallocated < 100
					continue

				# Apparently this dataset isn't consistent between its own CSV files, so
				# we need to hard-code some fixes...
				if state == 'Colorado' and county == "broomfield county and city":
					county = 'broomfield county'
				if state == 'Virginia' and county == "matthews county":
					county = "mathews county"


				if state == 'Alaska':
					if county == "wade hampton census area":
						wade_hampton = int(row[-1])
					elif county == "kusilvak census area":
						kusilvak = int(row[-1])

				if state in blacklist and county in blacklist[state]:
					continue

				if county not in states[state]:
					states[state][county] = {
						"covid": {}
					}

				assert f'{header[-1]}-{varname}' not in states[state][county]
				states[state][county]["covid"][f'{header[-1]}-{varname}'] = int(row[-1])

				# Add growth in covid deaths the week before lock downs started having an effect.
				if varname == 'deaths':
					if float(row[79-7]) > 0:
						states[state][county]["covid"][f'death-growth-rate-est'] = float(row[79])/float(row[79-7])
					else:
						states[state][county]["covid"][f'death-growth-rate-est'] = None

			# We distribute "unattributed New York deaths" proportional to how the other
			# covid deaths are distributed.
			total = states['New York']['new york county']["covid"][f'{header[-1]}-{varname}'] + states['New York']['bronx county']["covid"][f'{header[-1]}-{varname}'] + states['New York']['kings county']["covid"][f'{header[-1]}-{varname}'] + states['New York']['queens county']["covid"][f'{header[-1]}-{varname}'] + states['New York']['richmond county']["covid"][f'{header[-1]}-{varname}']
			states['New York']['new york county']["covid"][f'{header[-1]}-{varname}'] += new_york_unallocated * (states['New York']['new york county']["covid"][f'{header[-1]}-{varname}'] / total)
			states['New York']['bronx county']["covid"][f'{header[-1]}-{varname}'] += new_york_unallocated * (states['New York']['bronx county']["covid"][f'{header[-1]}-{varname}'] / total)
			states['New York']['kings county']["covid"][f'{header[-1]}-{varname}'] += new_york_unallocated * (states['New York']['kings county']["covid"][f'{header[-1]}-{varname}'] / total)
			states['New York']['queens county']["covid"][f'{header[-1]}-{varname}'] += new_york_unallocated * (states['New York']['queens county']["covid"][f'{header[-1]}-{varname}'] / total)
			states['New York']['richmond county']["covid"][f'{header[-1]}-{varname}'] += new_york_unallocated * (states['New York']['richmond county']["covid"][f'{header[-1]}-{varname}'] / total)

	# Wade Hampton and Kusilvak are the same cuonty but, for some reason, exist as two rows.  Since both rows have zero
	# deaths we won't worry about this for now... but if the rows ever differ we may want to email the CDC and ask why
	# they have duplicate rows.
	assert wade_hampton == kusilvak, 'If this is ever violated, we need to revisit how we resolve these duplicate rows'

	return states

merger.merge(get_covid())

def get_elections():
	states = {}
	fips_to_county = {
		'08014': ('broomfield county', 'Colorado')
	}
	with open(pjoin('data', 'fips_to_county.txt'), 'r') as f:
		for line in f.readlines():
			if len(line.strip()) == 0:
				continue
			code, county, state = line.strip().split('\t')
			# American Samoa, Northern Mariana Islands, Puerto Rico
			if state in ['AS', 'MP', 'PR']:
				continue
			fips_to_county[code] = (county.lower(), abbreviation_to_name[state])

	with open(pjoin('data', 'US_County_Level_Presidential_Results_08-16.csv'), 'r') as f:
		reader = csv.reader(f, delimiter=',')
		header = next(reader)
		assert header == ['fips_code', 'county', 'total_2008', 'dem_2008', 'gop_2008', 'oth_2008', 'total_2012', 'dem_2012', 'gop_2012', 'oth_2012', 'total_2016', 'dem_2016', 'gop_2016', 'oth_2016']
		rows = [row for row in reader]
		for row in rows:
			county, state = fips_to_county[row[0]]

			if state not in states:
				states[state] = {}

			all2008 = int(row[2])
			dem2008 = int(row[3])
			gop2008 = int(row[4])

			all2012 = int(row[6])
			dem2012 = int(row[7])
			gop2012 = int(row[8])

			all2016 = int(row[10])
			dem2016 = int(row[11])
			gop2016 = int(row[12])

			states[state][county] = {
				"elections": {
					"2008": {
						"total": all2008,
						"dem": dem2008,
						"gop": gop2008,
					},
					"2012": {
						"total": all2012,
						"dem": dem2012,
						"gop": gop2012,
					},
					"2016": {
						"total": all2016,
						"dem": dem2016,
						"gop": gop2016,
					}
				},
				"fips": row[0]
			}

	# Missing Alaska
	assert "Alaska" not in states
	states["Alaska"] = {}

	return states

merger.merge(get_elections(), missing={
	"Alaska": set(merger.states["Alaska"].keys()),
	"Hawaii": {"kalawao"}
})

with open('states.json', 'w+') as f:
	json.dump(merger.states, f, indent=1)


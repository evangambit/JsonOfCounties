# -*- coding: utf-8 -*-

import bson, code, copy, csv, json, math, os, re

from scipy.ndimage import filters
import shapefile

import matplotlib.pyplot as plt
import numpy as np

import os

pjoin = os.path.join

from shapely import geometry
from shapely.geometry import Point

import pandas as pd

def flatten_json(j, r = None, prefix = [], delimiter = '/'):
	if r is None:
		r = {}
	for k in j:
		assert delimiter not in k, k
		if type(j[k]) is dict:
			flatten_json(j[k], r, prefix + [k])
		else:
			r[delimiter.join(prefix + [k])] = j[k]
	return r

def pad(t, n, c=' '):
	t = str(t)
	return max(n - len(t), 0) * c + t

state_abbreviation_to_name = {
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

state_name_to_abbreviation = {}
for k in state_abbreviation_to_name:
	state_name_to_abbreviation[state_abbreviation_to_name[k]] = k

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

state_name_to_fips_code = {
	"Alabama": "01",
	"Alaska": "02",
	"Arizona": "04",
	"Arkansas": "05",
	"California": "06",
	"Colorado": "08",
	"Connecticut": "09",
	"Delaware": "10",
	"District of Columbia": "11",
	"Florida": "12",
	"Georgia": "13",
	"Hawaii": "15",
	"Idaho": "16",
	"Illinois": "17",
	"Indiana": "18",
	"Iowa": "19",
	"Kansas": "20",
	"Kentucky": "21",
	"Louisiana": "22",
	"Maine": "23",
	"Maryland": "24",
	"Massachusetts": "25",
	"Michigan": "26",
	"Minnesota": "27",
	"Mississippi": "28",
	"Missouri": "29",
	"Montana": "30",
	"Nebraska": "31",
	"Nevada": "32",
	"New Hampshire": "33",
	"New Jersey": "34",
	"New Mexico": "35",
	"New York": "36",
	"North Carolina": "37",
	"North Dakota": "38",
	"Ohio": "39",
	"Oklahoma": "40",
	"Oregon": "41",
	"Pennsylvania": "42",
	"Rhode Island": "44",
	"South Carolina": "45",
	"South Dakota": "46",
	"Tennessee": "47",
	"Texas": "48",
	"Utah": "49",
	"Vermont": "50",
	"Virginia": "51",
	"Washington": "53",
	"West Virginia": "54",
	"Wisconsin": "55",
	"Wyoming": "56",
	"American Samoa": "60",
	"Guam": "66",
	"Northern Mariana Islands": "69",
	"Puerto Rico": "72",
	"Virgin Islands": "78",
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

		i = 0
		while i < len(list1):
			county = list1[i].lower()
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

		list1.sort()
		list2.sort()

		if state not in missing:
			assert len(list1) == 0, f"{state}\n\n{list1}\n\n{list2}"
		else:
			assert len([x for x in list1 if x not in missing[state]]) == 0

		if not allow_missing:
			assert len(list2) - len(missing.get(state, {})) == 0, list2

		# Assert mapping is not many-to-1
		assert len(M.values()) == len(set(M.values()))

		return M

	def merge_with_fips(self, counties, missing=set()):
		kFipsConversions = {
			# Shannon County renamed to Oglala Lakota County
			"46113": "46102",

			# kusilvak census area renamed to wade hampton census area
			"02158": "02270",
		}
		for state_name in self.states:
			for county_name in self.states[state_name]:
				county = self.states[state_name][county_name]
				fips = county["fips"]
				if kFipsConversions.get(fips, None) in counties:
					fips = kFipsConversions[fips]
				if fips in missing:
					continue
				self.add_to_json(county, counties[fips])

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
			assert k not in base, f'base already has "{k}"'
			base[k] = addition[k]

def get_geometry():
	counties = {}

	sf = shapefile.Reader(pjoin('data', 'tl_2017_us_county/tl_2017_us_county.shp'))

	# Add geometric data for countries.
	for s in sf:
		state = fips_code_to_name[s.record.STATEFP]
		if state in not_states:
			continue
		fips = s.record.GEOID
		county_name = s.record.NAMELSAD.lower()

		# There is one county that crosses from negative
		# to positive longitudes, which screws up center-point
		# computations.  To fix this we subtact 360 from
		# positive longitudes.
		poly = geometry.Polygon([(x - 360 if x > 0 else x, y) for x, y in s.shape.points])

		# We explicitly compute centroids rather than use
		# s.record.INTPTLAT and s.record.INTPTLON, since
		# I can't find any documentation of how these
		# points are actually picked.  We use the convex
		# hull since some 'polygons' are weird, due to some
		# islands containing islands of territory (figuratively
		# and literally).
		center = poly.convex_hull.centroid

		counties[fips] = {
			"land_area (km^2)": s.record.ALAND / 1e6,
			"area (km^2)": (s.record.ALAND + s.record.AWATER) / 1e6,

			# NOTE: we don't undo the "- 360" transformation
			# above, since most use cases probably *prefer*
			# not having to deal with the wrapping behavior.
			"longitude (deg)": center.x,
			"latitude (deg)": center.y,
		}

	return counties

def get_zips():
	with open(pjoin('data', 'zip_county_fips_2018_03.csv'), 'r') as f:
		reader = csv.reader(f, delimiter=',')
		header = next(reader)
		rows = [row for row in reader]

	counties = {}

	for zipcode, fips, city, state, county, _ in rows:
		if state in ["PR", "GU", "VI"]:
			continue
		if fips not in counties:
			counties[fips] = {
				'zip-codes': []
			}
		counties[fips]['zip-codes'].append(zipcode)

  # kusilvak census area
	counties["02158"] = {
		"zip-codes": [
			"99554", "99563", "99581", "99585", "99604", "99620", "99632", "99650", "99657", "99658", "99662", "99666"
		]
	}
	# oglala lakota county
	counties["46113"] = {
		"zip-codes": [
			"57716", "57752", "57756", "57764", "57770", "57772", "57794",
		]
	}
	return counties

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

	# https://www2.census.gov/programs-surveys/popest/technical-documentation/file-layouts/2010-2019/cc-est2019-alldata.pdf
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
		"12": "7/1/2019",
	}
	# After downloading this file you should open it with a text editor (
	# I use Sublime) and re-encode it as utf8.

	counties = {}
	populations = {}

	with open(pjoin('data', 'cc-est2019-alldata.csv'), 'r') as f:
		reader = csv.reader(f, delimiter=',')
		header = next(reader)
		rows = [row for row in reader]
		assert header[:7] == ['SUMLEV', 'STATE', 'COUNTY', 'STNAME', 'CTYNAME', 'YEAR', 'AGEGRP']
		for row in rows:
			fips = row[1] + row[2]

			county = row[4].lower()
			year = year_code_to_year[row[5]].split('/')[-1]

			if fips not in populations:
				populations[fips] = {}

			age_group = int(row[6])
			total = int(row[7])

			if age_group == 0:
				populations[fips][year] = total

			# We only grab the latest year available and ignore the
			# other rows.
			if year_code_to_year[row[5]] != '7/1/2019':
				continue

			if age_group == 0:
				# age group "0" is everyone.  We grab racial data from
				# this row.  The racial break down done by the Census
				# Bureau is... intense, with 73 different columns.  To
				# keep the file size reasonable I don't track them all.
				# Fortunately the code and data is freely available so
				# it is trivial for you to add more columns if you like!

				# We assume this is the first row we see.
				assert fips not in counties
				counties[fips] = {}
				counties[fips]['race'] = {}
				counties[fips]['age'] = {}

				counties[fips]['male'] = int(row[8])
				counties[fips]['female'] = int(row[9])

				counties[fips]['population'] = total

				counties[fips]['race']['non_hispanic_white_alone_male'] = int(row[34]) / total
				counties[fips]['race']['non_hispanic_white_alone_female'] = int(row[35]) / total

				counties[fips]['race']['black_alone_male'] = int(row[12]) / total
				counties[fips]['race']['black_alone_female'] = int(row[13]) / total

				counties[fips]['race']['asian_alone_male'] = int(row[16]) / total
				counties[fips]['race']['asian_alone_female'] = int(row[17]) / total

				counties[fips]['race']['hispanic_male'] = int(row[56]) / total
				counties[fips]['race']['hispanic_female'] = int(row[57]) / total

			else:
				counties[fips]['age'][age_code_to_group[int(row[6])]] = int(row[7]) / counties[fips]['population']

	for fip in counties:
		counties[fip]['population'] = populations[fip]

	return counties

def get_cdc_deaths():
	counties = {}
	fns = [
		"Compressed Mortality, 1999-2019 (all suicides).txt",
		"Compressed Mortality, 1999-2019 (firearm suicides).txt",
		"Compressed Mortality (assaults), 1999-2019.txt",
		"Compressed Mortality (land vehicle deaths; ICD-10 codes V01-V89), 1999-2019.txt"
	]
	for varname, fn in zip(['suicides', 'firearm suicides', 'homicides', 'vehicle'], fns):
		with open(pjoin('data', 'CDC', fn), 'r') as f:
			reader = csv.reader(f, delimiter='\t', quotechar='"')
			rows = [row for row in reader]
		header = rows[0]
		rows = rows[1:]
		rows = rows[:rows.index(['---']) - 1]
		former_independent_cities = {}
		for row in rows:
			_, county, fips, deaths, _, _ = row
			county = county.lower()
			state = state_abbreviation_to_name[county.split(', ')[-1].upper()]
			county = ', '.join(county.split(', ')[:-1])

			# These counties changed their names recently, and rows with
			# both the old names and new names are found in the CDC
			# dataset, so we simply ignore these names.
			if county in ['prince of wales-outer ketchikan census area', 'skagway-hoonah-angoon census area', "wrangell-petersburg census area"]:
				continue

			if deaths == 'Suppressed':
				deaths = None
			elif deaths == 'Missing':
				deaths = -1
			else:
				deaths = int(deaths)

			if state in former_independent_cities_to_counties and county in former_independent_cities_to_counties[state]:
				county = former_independent_cities_to_counties[state][county]
				if state not in former_independent_cities:
					former_independent_cities[state] = {}
				former_independent_cities[state][county] = deaths
				continue

			if fips not in counties:
				counties[fips] = {
					"deaths": {}
				}
			assert varname not in counties[fips]["deaths"]
			counties[fips]["deaths"][varname] = deaths

		# Add formly independent cities to their respective counties.
		for state in former_independent_cities:
			for county in former_independent_cities[state]:
				# If either value was suppressed, we keep the concatenated
				# value as None.
				if counties[fips]["deaths"][varname] is None:
					continue
				if former_independent_cities[state][county] is None:
					continue
				counties[fips]["deaths"][varname] += former_independent_cities[state][county]

	return counties

# Labor force data
# https://www.bls.gov/lau/#cntyaa
def get_labor_force():
	counties = {}
	years = ['2004', '2008', '2012', '2016', '2020']
	for year in years:
		with open(pjoin('data', 'bls', year + '.txt'), 'r') as f:
			lines = f.readlines()
			for line in lines[6:]:
				line = line.strip()
				if len(line) == 0:
					break
				laus_code, state_fips_code, county_fips_code, county_name, year, labor_force, employed, unemployed, unemployment_rate = re.sub(r"  +", "  ", line).split("  ")
				if state_fips_code == '72':  # PR
					continue
				fips = state_fips_code + county_fips_code

				if fips not in counties:
					counties[fips] = {'bls': {}}
				c = {}
				c['labor_force'] = float(labor_force.replace(",",""))
				c['employed'] = float(employed.replace(",",""))
				c['unemployed'] = float(unemployed.replace(",",""))
				# NOTE: we exclude unemployment_rate since it is trivially computable as
				# "unemployed / labor_force"
				# c['unemployment_rate'] = float(unemployment_rate)
				counties[fips]['bls'][year] = c

	return counties

def get_fatal_police_shootings():
	states = {}
	for year in ['2017', '2018', '2019', '2020']:
		for varname in [f'total-{year}', f'unarmed-{year}', f'firearmed-{year}']:
			with open(pjoin('generated', 'police_shootings', varname + '.json'), 'r') as f:
				shootings = json.load(f)

				for k in shootings:
					state_name = state_abbreviation_to_name[k[-2:].upper()]
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

def get_police_deaths():
	states = {}

	with open(pjoin('data', 'police-deaths-2019.txt'), 'r') as f:
		lines = f.readlines()[8:]
	lines = [line.strip() for line in lines]
	F = {}
	for i in range(0, len(lines), 5):
		name = lines[i + 0]
		cause = lines[i + 2]
		F[cause] = F.get(cause, 0) + 1
		location = lines[i + 3]
		state = state_abbreviation_to_name[location[-2:]]
		county = location[:-4].lower()
		if state not in states:
			states[state] = {}
		if county not in states[state]:
			states[state][county] = {}
		states[state][county]['police_deaths'] = states[state][county].get('police_deaths', 0) + 1

	return states

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
				state = state_abbreviation_to_name[loc[-2:]]

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

def get_poverty():
	with open('data/poverty.tsv', 'r') as f:
		reader = csv.reader(f, delimiter='\t')
		header = next(reader)
		rows = [row for row in reader]

	fipsIdx = header.index('FIPStxt')
	povertyIdx = header.index('PCTPOVALL_2019')

	fips2poverty = {}
	for row in rows:
		p = row[povertyIdx]
		p = p.replace(',', '')
		fips2poverty[row[fipsIdx]] = {
			'poverty-rate': float(p)
		}
	return fips2poverty

def get_education():
	with open('data/education.tsv', 'r') as f:
		reader = csv.reader(f, delimiter='\t')
		header = next(reader)
		rows = [row for row in reader]

	fipsIdx = header.index('FIPS Code')
	lessThanHighSchoolIdx = header.index('Percent of adults with less than a high school diploma, 2015-19')
	highSchoolIdx = header.index('Percent of adults with a high school diploma only, 2015-19')
	someCollegeIdx = header.index("Percent of adults completing some college or associate's degree, 2015-19")
	bachelorsIdx = header.index("Percent of adults with a bachelor's degree or higher, 2015-19")

	fips2edu = {}
	for row in rows:
		A = {
				'less-than-high-school': row[lessThanHighSchoolIdx],
				'high-school': row[highSchoolIdx],
				'some-college': row[someCollegeIdx],
				'bachelors+': row[bachelorsIdx]
		}
		for k in A:
			if A[k] == '':
				A[k] = None
			else:
				A[k] = float(A[k])
		fips2edu[row[fipsIdx]] = { 'edu': A }

	return fips2edu

def get_covid():
	fips2covid = {}

	for varname, fn in zip(['deaths', 'confirmed'], ['covid_deaths_usafacts.csv', 'covid_confirmed_usafacts.csv']):
		with open(pjoin('data', fn), 'r') as f:
			reader = csv.reader(f, delimiter=',')
			header = next(reader)

			countyColumn = header.index('countyFIPS')
			stateColumn = header.index('State')

			rows = [row for row in reader]
			for row in rows:
				for date in [date for date in header if re.match(r"\d{4}-\d\d-01", date)]:
					column = header.index(date)
					fips = row[countyColumn]

					if fips == '0':
						 # Unallocated cases make up a vanishingly small proportion of data.
						continue

					if len(fips) == 4:
						fips = '0' + fips

					if fips not in fips2covid:
						fips2covid[fips] = {}
					if f"covid-{varname}" not in fips2covid[fips]:
						fips2covid[fips][f"covid-{varname}"] = {}

					assert date not in fips2covid[fips][f"covid-{varname}"], (date, fips)
					fips2covid[fips][f"covid-{varname}"][date] = int(row[column])

	with open(pjoin('data', 'COVID-19_Vaccinations_in_the_United_States_County.csv'), 'r') as f:
		reader = csv.reader(f, delimiter=',')
		header = next(reader)
		rows = [row for row in reader]

	def fix_vac_date(date):
		month, day, year = date.split('/')
		return '-'.join([year, month, day])

	for row in rows[::-1]:
		fips = row[1]
		if not re.match(r"^\d\d/01/2021$", row[0]):
			continue
		if fips not in fips2covid:
			continue
		if 'covid-vaccination' not in fips2covid[fips]:
			fips2covid[fips]['covid-vaccination'] = {}
		fips2covid[fips]["covid-vaccination"][fix_vac_date(row[0])] = float(row[5])

	return fips2covid

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
			fips_to_county[code] = (county.lower(), state_abbreviation_to_name[state])

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
				}
			}

	# Missing Alaska
	assert "Alaska" not in states
	states["Alaska"] = {}

	return states

def get_weather(kStates):
	"""
	Value flags (which we ignore):
    C = complete (all 30 years used)
    S = standard (no more than 5 years missing and no more than 3 consecutive 
        years missing among the sufficiently complete years)
    R = representative (observed record utilized incomplete, but value was scaled
        or based on filled values to be representative of the full period of record)
    P = provisional (at least 10 years used, but not sufficiently complete to be 
        labeled as standard or representative). Also used for parameter values on 
        February 29 as well as for interpolated daily precipitation, snowfall, and
        snow depth percentiles. 
    Q = quasi-normal (at least 2 years per month, but not sufficiently complete to 
        be labeled as provisional or any other higher flag code. The associated
        value was computed using a pseudonormals approach or derived from monthly
        pseudonormals.
	"""
	stations = {}
	for varname, fn in [
			("prcp", "ann-prcp-normal.txt"),
			("snow", "ann-snow-normal.txt"),
			("temp", "ann-tavg-normal.txt"),
			("altitude", "ghcnd-stations.txt"),
			("monthy-temp", "mly-tavg-normal.txt")
		]:
		with open(pjoin("data", "noaa-weather", fn), "r") as f:
			for line in f.readlines():
				if fn != 'ghcnd-stations.txt':
					cells = re.split(r"\s+", line.strip())
					station = cells[0]
					vals = cells[1:]
					for val in vals:
						assert val[-1] in "CSRPQ", repr(val)
					val0 = float(vals[0][:-1])
					if station not in stations:
						stations[station] = {}
					if varname == "prcp":
						stations[station][varname] = val0 / 100.0
					elif varname == "snow":
						stations[station][varname] = None if val0 < 0.0 else val0 / 10.0
					elif varname == "temp":
						stations[station][varname] = val0 / 10.0
					elif varname == "monthy-temp":
						assert len(vals) == 12, repr(vals)
						stations[station]['temp-jan'] = float(vals[0][:-1]) / 10.0
						stations[station]['temp-apr'] = float(vals[3][:-1]) / 10.0
						stations[station]['temp-jul'] = float(vals[6][:-1]) / 10.0
						stations[station]['temp-oct'] = float(vals[9][:-1]) / 10.0
					else:
						assert False
				else:
					line = re.split(' +', line.strip())[:4]
					station, longitude, latitude, altitude = line
					if altitude == '-999.9':  # skip null value
						continue
					longitude = float(longitude)
					latitude = float(latitude)
					altitude = float(altitude)
					if station not in stations:
						stations[station] = {}
					stations[station][varname] = altitude

	# Read station locations.
	with open(pjoin("data", "noaa-weather", "ghcnd-stations.txt"), "r") as f:
		lines = f.readlines()
		# Filter out stations that don't give us any data.
		lines = [line for line in lines if line.split(' ')[0] in stations]
		# station, latitude, longitude, elevation, ...
		lines = [re.split(r" +", line.strip()) for line in lines]
	station_locations = [(float(line[1]), float(line[2])) for line in lines]
	station_locations = np.array(station_locations)

	fips2location = {}
	for sn in kStates:
		for cn in kStates[sn]:
			c = kStates[sn][cn]
			fips2location[c['fips']] = (c['latitude (deg)'], c['longitude (deg)'])

	with open(pjoin("data", "noaa-weather", "fips_to_stations.json"), "r") as f:
		fips2stations = json.load(f)

	kAllVarnames = [
		'prcp', 'snow', 'temp', 'altitude', 'temp-jan', 'temp-apr', 'temp-jul', 'temp-oct'
	]

	fips2weather = {}
	for fips in fips2stations:
		if fips[:2] == '72':  # Ignore Puerto Rico
			continue

		validVals = {}
		for vname in kAllVarnames:
			validVals[vname] = []
		for station_name in fips2stations[fips]:
			if station_name not in stations:
				continue
			station = stations[station_name]
			for varname in station:
				if station[varname] is None:
					continue
				validVals[varname].append(station[varname])

		noaa = {}
		for varname in validVals:
			if len(validVals[varname]) == 0:
				noaa[varname] = None
			else:
				noaa[varname] = sum(validVals[varname]) / len(validVals[varname])

		if fips == '02270':  # Wade Hampton Area renamed
			fips = '02158'
		for k in noaa:
			if noaa[k] is not None:
				continue
			# If fips isn't in fips2location then we're not even
			# including the county in the dataset, so we can ignore
			# it.
			if fips not in fips2location:
				print('yyy', fips)
				noaa[k] = None
				continue
			# If we cannot find a value from a station within a
			# county, we look for the nearest station.

			loc = fips2location[fips]
			I = np.argsort(((station_locations - np.array(loc))**2).sum(1))
			for i in I:
				station_name = lines[i][0]
				station = stations[station_name]
				if k in station and station[k] is not None:
					noaa[k] = station[k]
					break

		for k in noaa:
			if k not in noaa or noaa[k] is None:
				print(fips)
			noaa[k] = round(noaa[k] * 10) / 10

		fips2weather[fips] = {
			"noaa": noaa
		}

	return fips2weather

daysBeforeMonth = [
	0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31
]
daysBeforeMonth = np.cumsum(daysBeforeMonth)

kAllFips = set()
with open('base.json', 'r') as f:
	base = json.load(f)
for state_name in base:
	for country_name in base[state_name]:
		kAllFips.add(base[state_name][country_name]['fips'])

def get_expenses():
	def dollar2float(x):
		return float(x.replace('$', '').replace(',', ''))
	with open(pjoin('generated', 'living-wage.json'), 'r') as f:
		J = json.load(f)
	r = {}
	for fips in J:
		j = J[fips]
		r[fips] = {
			"cost-of-living": {
				"living_wage": dollar2float(j['livingWage-1-adult']),
				"food_costs": dollar2float(j['expenses']['food-1-adult']),
				"medical_costs": dollar2float(j['expenses']['medical-1-adult']),
				"housing_costs": dollar2float(j['expenses']['housing-1-adult']),
				"tax_costs": dollar2float(j['expenses']['taxes-1-adult']),
			}
		}
	return r

def get_industry():
	with open(pjoin('data', 'County_Business_Patterns.csv'), 'r') as f:
		reader = csv.reader(f, delimiter=',')
		header = next(reader)
		rows = [row for row in reader][1:]
	r = {}
	for row in rows:
		fips = row[0].split('US')[1]
		sector = row[5]
		if sector == 'Total for all sectors':
			continue
		if row[9] != 'All establishments':
			continue
		payroll = int(row[12]) * 1000
		numEmployees = int(row[16])
		if fips not in r:
			r[fips] = {'industry': {}}
		r[fips]['industry'][sector] = {
			'payroll': payroll,
			'employees': numEmployees
		}
	return r


def get_health():
	with open(pjoin('generated', 'county-health.csv'), 'r') as f:
		reader = csv.reader(f, delimiter=',')
		header = next(reader)
		rows = [row for row in reader][1:]
	r = {}
	for row in rows:
		fips = row[0]
		h = {}
		for i in range(1, len(row)):
			h[header[i]] = float(row[i])
		r[fips] = {
			'health': h
		}
	return r

def get_life_expectancy():
	with open(pjoin('data', 'Life Expectancy And Mortality Risk By County 1980-2014.csv'), 'r') as f:
		reader = csv.reader(f, delimiter='\t')
		header = next(reader)
		header = next(reader)
		rows = [row for row in reader]
	states = list(state_abbreviation_to_name.values())
	x = header.index('Life expectancy, 2014*')

	r = {}
	for row in rows[1:]:
		name = row[0]
		fips = row[1]
		if name in states or fips == '':
			continue
		if len(fips) < 5:
			fips = '0' + fips
		r[fips] = {
			'life-expectancy': float(re.findall(r"[\d\.]+", row[x])[0])
		}

	return r

if __name__ == '__main__':
	merger = CountyNameMerger()

	merger.merge_with_fips(get_geometry())

	merger.merge_with_fips(get_weather(merger.states))

	# A = []
	# states = {}
	# sf = shapefile.Reader(pjoin('data', 'SpatialJoin_CDs_to_Counties_Final.shp'))
	# for i, s in enumerate(sf):
	# 	if s.record.STATE_NAME not in states:
	# 		states[s.record.STATE_NAME] = {}
	# 	r = s.record
	# 	states[r.STATE_NAME][r.NAME] = {
	# 		"noaa": {
	# 			"males": r.MALES,
	# 			"females": r.FEMALES,
	# 			"families": r.FAMILIES,
	# 			"asian": r.ASIAN,
	# 			"black": r.BLACK,
	# 			"hispanic": r.HISPANIC,
	# 			"white": r.WHITE,
	# 			"mult_race": r.MULT_RACE,
	# 			"households": r.HOUSEHOLDS,
	# 			"median_age": r.MED_AGE,
	# 			"median_age_male": r.MED_AGE_M,
	# 			"median_age_female": r.MED_AGE_F,
	# 			"average_family_size": r.AVE_FAM_SZ,
	# 		}
	# 	}
	# 	A.append(r.AVE_FAM_SZ)

	merger.merge_with_fips(get_zips())
	merger.merge_with_fips(get_demographics())
	merger.merge_with_fips(get_cdc_deaths())
	merger.merge_with_fips(get_labor_force(), missing=set(["02201", "02232", "02280", "02105", "02195", "02198", "02230", "02275", "15005"]))
	merger.merge_with_fips(get_life_expectancy())

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
			for year in ['2017', '2018', '2019', '2020']:
				if f"total-{year}" not in merger.states[state][county]["fatal_police_shootings"]:
					merger.states[state][county]["fatal_police_shootings"][f"total-{year}"] = 0
				if f"unarmed-{year}" not in merger.states[state][county]["fatal_police_shootings"]:
					merger.states[state][county]["fatal_police_shootings"][f"unarmed-{year}"] = 0
				if f"firearmed-{year}" not in merger.states[state][county]["fatal_police_shootings"]:
					merger.states[state][county]["fatal_police_shootings"][f"firearmed-{year}"] = 0

	# We do the same thing for police deaths.
	merger.merge(get_police_deaths(), allow_missing=True)
	for state in merger.states:
		for county in merger.states[state]:
			if 'police_deaths' not in merger.states[state][county]:
				merger.states[state][county]['police_deaths'] = 0

	merger.merge(get_avg_income())
	merger.merge_with_fips(get_covid())

	# We're missing election data for Alaska and Kalawao County, HI
	merger.merge(get_elections(), missing={
		"Alaska": set(merger.states["Alaska"].keys()),
		"Hawaii": {"kalawao"}
	})

	merger.merge_with_fips(get_education())
	merger.merge_with_fips(get_poverty(), missing={'15005'})

	# Terrible hack for 2020
	with open(pjoin('data', 'election2020.json'), 'r') as f:
		e2020 = json.load(f)
	merger.merge(e2020, missing={
		"Alaska": set(merger.states["Alaska"].keys()),
		"Hawaii": {"kalawao"}
	})

	for sn in merger.states:
		if sn == 'Alaska':
			continue
		for cn in merger.states[sn]:
			if sn == 'Hawaii' and cn == 'kalawao county':
				continue
			c = merger.states[sn][cn]
			e20 = c['2020e']
			del c['2020e']
			c['elections']['2020'] = e20

	merger.merge_with_fips(get_expenses())
	merger.merge_with_fips(get_industry(), missing={
		'48269', '15005', '31007', '31117', '48301', '48033', '32009', '30069'
	})

	# Washington DC missing
	merger.merge_with_fips(get_health(), missing={'11001'})

	# Convert from { "Alabama": { "clay county": { "fips": "01027" } } } to [ { "fips": "01027", name": "clay county", "state": "AL" } ]
	counties = []
	for stateName in merger.states:
		state = merger.states[stateName]
		for countyName in state:
			county = state[countyName]
			fips = county['fips']
			assert 'name' not in county
			county['name'] = countyName
			assert 'state' not in county
			county['state'] = state_name_to_abbreviation[stateName]
			counties.append(county)

	# Create new dictionary for each county so that important keys (name, fips, etc.) are at the front.
	for i, county in enumerate(counties):
		c = {}
		for k in ['name', 'fips', 'state']:
			c[k] = county[k]
		for k in county:
			c[k] = county[k]
		counties[i] = c

	with open('counties.json', 'w+') as f:
		json.dump(counties, f, indent=1)

	with open('counties.json', 'r') as f:
		counties = json.load(f)

	df = pd.json_normalize([flatten_json(county) for county in counties])
	df.to_csv('counties.csv', index=False)

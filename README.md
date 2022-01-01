# County-level Data

This is a repository of various data, broken down by US county.

While most of this repository is dedicated to providing the data and code that I used to produce the final dataset, the dataset itself is simply "counties.json".

An example entry:

```JavaScript
[
  // ...
  {
    "name": "waukesha county",
    "fips": "55133",
    "state": "WI",
    "land_area": 1423.675192,
    "area": 1503.52665,
    "longitude": -88.3041411471765,
    "latitude": 43.01843887416162,
    "noaa": {
      "prcp": 35.03,
      "snow": 39.5,
      "temp": 46.53333333333333
    },
    "zip-codes": [
      "53186",
      "53018",
      // ...
      "53187"
    ],
    "race": {
      "non_hispanic_white_alone_male": 0.4318527058520824,
      "non_hispanic_white_alone_female": 0.44800568038436606,
      "black_alone_male": 0.009233098629879416,
      "black_alone_female": 0.008310283573892003,
      "asian_alone_male": 0.01858247690488325,
      "asian_alone_female": 0.01985413089624392,
      "hispanic_male": 0.024772512481506588,
      "hispanic_female": 0.02434450442604862
    },
    "age": {
      "0-4": 0.05157868173518919,
      "5-9": 0.05712546821112425,
      // ...
      "80-84": 0.022882349739484113,
      "85+": 0.0260045819128249
    },
    "male": 198880,
    "female": 205318,
    "population": {
      "2010": 390028,
      "2011": 390837,
      // ...
      "2019": 404198
    },
    "deaths": {
      "suicides": 722,
      "firearm suicides": 341,
      "homicides": 65,
      "vehicle": 301
    },
    "bls": {
      "2004": {
        "labor_force": 212347.0,
        "employed": 203341.0,
        "unemployed": 9006.0
      },
      "2008": {
        "labor_force": 214460.0,
        "employed": 205879.0,
        "unemployed": 8581.0
      },
      "2012": {
        "labor_force": 217605.0,
        "employed": 205086.0,
        "unemployed": 12519.0
      },
      "2016": {
        "labor_force": 225184.0,
        "employed": 217425.0,
        "unemployed": 7759.0
      }
    },
    "fatal_police_shootings": {
      "total-2017": 1.0,
      "unarmed-2017": 0.0,
      "firearmed-2017": 1.0,
      "total-2018": 0.0,
      "unarmed-2018": 0.0,
      "firearmed-2018": 0.0,
      "total-2019": 1.0,
      "unarmed-2019": 0.0,
      "firearmed-2019": 0.0
    },
    "police_deaths": 0,
    "avg_income": 72650,
    "covid-deaths": {
      "2020-05-04": 20,
      "2020-05-11": 23,
      // ...
      "2021-01-04": 344
    },
    "covid-confirmed": {
      "2020-05-04": 367,
      "2020-05-11": 409,
      // ...
      "2021-01-04": 37600
    },
    "driving": {
      "2020-01-13": 107,
      "2020-01-27": 107,
      // ...
      "2020-12-28": 100
    },
    "walking": {
      "2020-01-13": 104,
      "2020-01-27": 108,
      // ...
      "2020-12-28": 141
    },
    "elections": {
      "2008": {
        "total": 232897,
        "dem": 85339,
        "gop": 145152
      },
      // ...
      "2020": {
        "total": 267214,
        "dem": 103906,
        "gop": 159649
      }
    }
    "edu": {
      "less-than-high-school": 3.8,
      "high-school": 22.7,
      "some-college": 29.1,
      "bachelors+": 44.5
    }
    "poverty-rate": 4.7,
    "cost-of-living": {
      "living_wage": 14.32,
      "food_costs": 3246.0,
      "medical_costs": 2754.0,
      "housing_costs": 7536.0,
      "tax_costs": 6319.0
    },
    "industry": {
      "Agriculture, forestry, fishing and hunting": {
        "payroll": 942000,
        "employees": 32
      },
      // ...
      "Industries not classified": {
        "payroll": 197000,
        "employees": 6
      }
    }
  },
  // ...
]
```

## Sources

1. State geometry (location, area, etc.) comes from data.gov, specifically [here](https://catalog.data.gov/dataset/tiger-line-shapefile-2017-nation-u-s-current-county-and-equivalent-national-shapefile) (download "Shapefile Zip File").  This data is NOT included in the repository because it is 122 MB; you may download it from the source, or from Google Drive [here](https://drive.google.com/file/d/1RvdPYAx3l0wJeGwNEfDnFOZafthqS4_b/view?usp=sharing).  Regardless of where you download it from, save the corresponding directory inside the "data" directory.

2. Population and demographics comes from the Census Bureau from a 2018 table ([here](https://www.census.gov/data/tables/time-series/demo/popest/2010s-counties-detail.html#par_textimage_1383669527)) (you need to re-encode it as utf-8).  This "United States" csv file is NOT included, as it is 154 MB, but can be downloaded from Google Drive [here](https://drive.google.com/file/d/11k-YAy4SM36jbXYUy5pylgo0mE-ZKudZ/view?usp=sharing).

3. Deaths, suicides, and homicides come from the [CDC's website](https://wonder.cdc.gov/mcd.html), where you can request the totals for each county.  We manually requested totals for all deaths, suicides, firearm suicides, and homicides.  Adding other causes of deaths is easy if you can give us the [ICD-10 Codes](https://wonder.cdc.gov/wonder/help/cmf.html#ICD-10%20Codes) you're interested in.  This is the source of the vast majority of missing data (marked as null in the JSON), since the CDC suppresses data from counties when there are fewer than 10 cases.  Adult obesity rates for each state also comes from the CDC [here](https://www.cdc.gov/obesity/data/prevalence-maps.html#race), though New Jersey is missing so it's obesity rate comes from [here](https://www-doh.state.nj.us/doh-shad/indicator/complete_profile/Obese.html?ListCategoryFirst=x#:~:text=The%20age%2Dadjusted%20prevalence%20of%20obesity%20among%20New%20Jersey%20adults,to%2030.6%25%20for%20U.S.%20adults.).

4. Labor statistics comes from [here](https://www.bls.gov/lau/#cntyaa) (the BLS).

5. Police shootings data comes from the [Washington Post's dataset](https://github.com/washingtonpost/data-police-shootings) and includes shootings from 2017 to 2020 (inclusive).  To convert from city (which is typically how the Washington Post reports) to county a variety of methods were used.  Of particular importance was the [City-to-County finder](http://www.stats.indiana.edu/uspr/a/place_frame.html) by [Stats Indiana](http://www.stats.indiana.edu/), which let me automatically map counties to cities.  Frequently cities belonged to several counties, in which case the shootings were distributed fractionally.  Where their tool failed (e.g. sometimes the location of a shooting is ambiguous, or wasn't in/near a large city), I was forced to determine location by hand, either from news articles or via Randy Major's [County Lines on Google Maps](https://www.randymajors.com/p/countygmap.html) page.  There are 19 shootings I still need to manually find counties for (these shootings are omitted).

6. Average income comes from the BEA [here](https://apps.bea.gov/regional/downloadzip.cfm).  I don't trust the median income estimates (there are some really crazy counties...), so I only report the average income.

7. Covid data comes from [this site](https://usafacts.org/visualizations/coronavirus-covid-19-spread-map/) on usafacts.org, who says their data comes from the CDC.  Vaccination rates [come from the CDC directly](https://data.cdc.gov/Vaccinations/COVID-19-Vaccinations-in-the-United-States-County/8xkx-amqh?fbclid=IwAR2SRG8olMOfVVz2-zCKd0Yz_24f1uQYCN6rbJxjyPhCSKZOwGWcoIMgFto) (and is not included in the repository due to its size).

8. Most Presidential election data comes this [github repository](https://github.com/tonmcg/US_County_Level_Election_Results_08-16/blob/master/US_County_Level_Presidential_Results_08-16.csv) which aggregates from a variety of sources, with credit to Tony McGovern, Bill Morris, The Guardian, townhall.com, and others.  Alaskan boroughs and census areas are missing, as is Kalawao County, Hawaii.

9. The mapping from counties to zip codes is from data.world [here](https://data.world/niccolley/us-zipcode-to-county-state), specifically Nic Colley, and is in the Public Domain.

10. Driving mobility data comes from Apple [here](https://www.apple.com/covid19/mobility), which they released to help analyze covid-19.  (Note that these are not absolute measures of mobility, so they are not directly comparable between counties).

11. Weather data comes from the NOAA (see data/noaa-weather/README.md for details).  Temperature is given in Fahrenheight and length is given in inches.  It's not clear why some regions have more snowfall than precipitation.  This would seem to suggest that either snowfall doesn't count as "precipitation" in these measurements, or they're doing something like switching between melted and unmelted measurements. Altitude is the average altitude of a weather station.  This is clearly not the same as the average altitude of the county (which I don't think is available – the USGS doesn't provide it at least) but should hopefully serve as a crude proxy.

12. [Educational attainment and poverty-rates](https://www.ers.usda.gov/data-products/county-level-data-sets/download-data/) are from the Census Bureau but prepared by the USDA.

13. Cost of living is provided by Amy Glasmeier at https://livingwage.mit.edu/ for households with 1 adult and 0 children.  She gets her data from the Bureau of Labor Statistics.

14. Country industry data ("data/County_Business_Patterns.csv") is from the Census Bureau from https://data.census.gov/cedsci/table?q=CBP2019.CB1900CBP&g=0100000US.050000&n=N0200.00&tid=CBP2019.CB1900CBP&hidePreview=true&nkd=EMPSZES~001,LFO~001 and is not included in the repo because it is large (44MB) but is available in Google Drive [here](https://drive.google.com/file/d/1QIDt6uNEARaNrQK0db0jrMsVgY27soWs/view?usp=sharing).

15. County health data from [County Health Rankings](https://www.countyhealthrankings.org) ([credits](https://www.countyhealthrankings.org/credits))

16. Life expectancy from the [Institute for Health Metrics and Evaluation](http://ghdx.healthdata.org/us-data) which I've copied to [this google sheet](https://docs.google.com/spreadsheets/d/14Z6waBMXiKBTRjYkCHo_HsIaXpwjVgfU/edit?usp=sharing&ouid=112327010154857432489&rtpof=true&sd=true)

Note that this "counties.json" does NOT contain a superset of each data source.  For instance the racial/age demographic breakdown provided by "cc-est2019-alldata.csv" is extremely specific (giving race/sex break downs for every age bucket for the last 9 years!) but we don't include all of that in counties.json.

Fortunately, it shouldn't be too hard for somebody with some Python experience to modify "create_json.py" to add whatever additional data they might need.

## How to (Re)Generate

Run

```Bash
# If you change fatal-police-shootings.csv or get_county_shootings.py
$ python get_county_shootings.py

# Generates living-wage.json. Takes 1.7 hours from scratch using 0.5 qps.
$ python generate_living_wage_data.py

# Generates county-health.csv. Takes 1 minute.
$ python generate_health_data.py

$ python create_json.py
```

*ONLY THE LAST COMMAND* is typically required.  The output of the other commands are included in the repo (`generated/police_shootings` and `living-wage.json`), so you shouldn't have to regenerate them.

## APA Citations

Apple. (2020, July 24). COVID‑19 - Mobility Trends Reports. COVID‑19 - Mobility Trends Reports. https://www.apple.com/covid19/mobility

Bureau of Economic Analysis. (2020). BEA : Regional Economic Accounts: Download. BEA : Regional Economic Accounts. https://apps.bea.gov/regional/downloadzip.cfm
Covid cases/deaths:

Bureau of Labor Statistics. (2019). Local Area Unemployment Statistics Home Page. Local Area Unemployment Statistics. https://www.bls.gov/lau/#cntyaa

Centers for Disease Control and Prevention. (2016). Compressed Mortality, 1999-2016 Request. Centers for Disease Control and Prevention (CDC). https://wonder.cdc.gov/mcd.html

Colley, N. (2020). US Zipcode to County State to FIPS Look Up. Data.World. https://data.world/niccolley/us-zipcode-to-county-state

County Health Rankings & Roadmaps. (2021).  University of Wisconsin Population Health Institute  https://www.countyhealthrankings.org/about-us

Glasmeier, Amy K. Living Wage Calculator. 2020. Massachusetts Institute of Technology. livingwage.mit.edu. Please describe any changes or transformations that were made to the data.

Institute for Health Metrics and Evaluation.  (2014).  United States Life Expectancy and Age-specific Mortality Risk by County. http://ghdx.healthdata.org/us-data

McGovern, Anthony and Morris, Bill (2016). US County Level Presidential Results. Retrieved from: https://github.com/tonmcg/US_County_Level_Election_Results_08-16

US Census Bureau. (2019). TIGER/Line Shapefile, 2017, nation, U.S., Current County and Equivalent National Shapefile - Data.gov. DATA.GOV. https://catalog.data.gov/dataset/tiger-line-shapefile-2017-nation-u-s-current-county-and-equivalent-national-shapefile

US Census Bureau. (2018). County Population by Characteristics: 2010-2019. The United States Census Bureau. https://www.census.gov/data/tables/time-series/demo/popest/2010s-counties-detail.html#par_textimage_1383669527

US Census Bureau. (2019). CBP2019.CB1900CBP_data_with_overlays_2021-06-25T123104.csv.  The US Census Bureau. https://data.census.gov/cedsci/table?q=CBP2019.CB1900CBP&g=0100000US.050000&n=N0200.00&tid=CBP2019.CB1900CBP&hidePreview=true&nkd=EMPSZES~001,LFO~001

U.S. Department of Agriculture. (2021). Educational attainment for the U.S., States, and counties, 1970-2019. The United States Department of Agriculture. https://www.ers.usda.gov/data-products/county-level-data-sets/download-data/

USAFacts. (2020, August 11). US Coronavirus Cases and Deaths. USAFacts.Org. https://usafacts.org/visualizations/coronavirus-covid-19-spread-map/

Washington Post. (2020). washingtonpost/data-police-shootings. GitHub. https://github.com/washingtonpost/data-police-shootings


# County-level Data

This is a working repository of data broken down by US county.

While most of this repositoory is dedicated to providing the data and code that we used to produce the final dataset, the dataset itself is simply states.json.  An example entry:

```JavaScript
{
  // ...
  "Nebraska": {
    // ...
    "holt county": {
      // Area is computed as if longitude and latitude were (x, y) coordinates. This is
      // naive, but should suffice for rough population density estimates.
      "area": 0.68525076424703,
      // Location is the average latitude/longitude of the vertices bounding the county.
      "location": [
       -98.66118420812809,
       42.4859272567734
      ],
      // Smallest latitude/longitude values in the county.
      "min_loation": [
       -99.25703899999999,
       42.087894999999996
      ],
      // largest latitude/longitude values in the county.
      "max_loation": [
       -98.300212,
       42.896724
      ],
      // The Census Bureau has a lot more than this.  It should be easy to add them
      // in the script if you need them.
      "race_demographics": {
       "non_hispanic_white_alone_male": 0.4622715661230104,
       "non_hispanic_white_alone_female": 0.4660051090587542,
       "black_alone_male": 0.0020632737276478678,
       "black_alone_female": 0.0017685203379838867,
       "asian_alone_male": 0.0021615248575358615,
       "asian_alone_female": 0.003340538416191786,
       "hispanic_male": 0.02859107879740617,
       "hispanic_female": 0.024071526822558458
      },
      // Percent of the population in each age bucket.
      "age_demographics": {
       "0-4": 0.07044606012969148,
       "5-9": 0.0734918451562193,
       "10-14": 0.07142857142857142,
       "15-19": 0.05570839064649243,
       "20-24": 0.0500098251129888,
       "25-29": 0.04725879347612497,
       "30-34": 0.04951856946354883,
       "35-39": 0.0546276282177245,
       "40-44": 0.04666928669679701,
       "45-49": 0.046865788956573,
       "50-54": 0.056494399685596386,
       "55-59": 0.08351346040479465,
       "60-64": 0.078109648260955,
       "65-69": 0.06543525250540382,
       "70-74": 0.048143053645116916,
       "75-79": 0.039791707604637454,
       "80-84": 0.027706818628414228,
       "85+": 0.03478089998034977
      },
      // Number of people.
      "male": 5088,
      "female": 5090,
      "population": 10178,
      // Number of suicides in 2016 (from the CDC).
      "suicides": "17",
      "firearm suicides": "12",
      // BLS labor statistics.
      "labor_force": "5,763",
      "employed": "5,613",
      "unemployed": "150",
      "unemployment_rate": "2.6",
      // Washington Post fatal police shootings statistics.
      "fatal_police_shootings": 0,
      "unarmed_fatal_police_shootings": 0,
      "fatal_police_shootings_where_victim_had_firearm": 0,
      // BEA-estimated average income in the county.
      "avg_income": 51404
    },
    // ...
  },
  // ...
}
```

If you want to use this data, feel free to (all the sources, except the Washington Post, are .gov websites), but please let me know (it's nice to know my work is being used).  You can email me ${myGithubUsername}@gmail, or just open an issue on Github.

## Sources

1. State geometry (location, area, etc.) is computed from data.gov, specifically [here](https://catalog.data.gov/dataset/tiger-line-shapefile-2017-nation-u-s-current-county-and-equivalent-national-shapefile).  This data is NOT included in the repository because if is 122 MB.  State areas are computed naively, assuming longitude/latitude are x/y coordinates.  As a result they're not particularly accurate (because longitude sizes vary based on location) but should be useful for computing population density.  Some day I hope to get around to computing them [accurately](https://stackoverflow.com/questions/1340223/calculating-area-enclosed-by-arbitrary-polygon-on-earths-surface) (or a helpful Internet stranger like yourself might do it for me).

2. Population and demographics comes from the Census Bureau from a 2018 table ([here](https://www.census.gov/data/tables/time-series/demo/popest/2010s-counties-detail.html#par_textimage_1383669527)).  This csv file is NOT included, as it is 154 MB.

3. Deaths, suicides, and firearm suicides come from the [CDC's website](https://wonder.cdc.gov/cmf-icd10.html), where you can request the totals for each county.  We manually requested totals for all deaths, all suicides, and firearm suicides, but adding other causes of deaths is easy if you can give us the [ICD-10 Codes](https://wonder.cdc.gov/wonder/help/cmf.html#ICD-10%20Codes) you're interested in.  This is the source of the vast majority of missing data (marked as null in the JSON), since the CDC suppresses data from counties with sufficiently few cases. 

4. Labor statistics comes from [here](https://www.bls.gov/lau/#cntyaa) (the BLS).

5. Police shootings data comes from the [Washington Post's dataset](https://github.com/washingtonpost/data-police-shootings).  In cases where the county is ambiguous, shootings are distributed fractionally.

6. Average income comes from the BEA [here](https://apps.bea.gov/regional/downloadzip.cfm).  I don't trust the median income estimates (there are some really crazy counties...), so I only report the average income.

Note that this "states.json" does NOT contain a superset of each data source.  For instance the racial/age demographic breakdown provided by "cc-est2018-alldata.csv" is extremely specific (giving race/sex break downs for every age bucket for 9 years!) but we don't include all of that in states.json.

Fortunately, it shouldn't be hard for somebody with some Python experience to modify "create_json.py" to add whatever additional data they might need.

## Why

I was originally trying to reproduce [this paper](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6391295/?fbclid=IwAR2Y0h6D-cEWXqk4_dooBX2MgUUrADyEIHN6iQFmbDc1qXf0MYHK3qWbUPo) (it reproduced!) and then I wanted to try and reproduce it with county-level data (since 3000 is a much larger sample size than 50).

This effort formed the base of this project, and I figured, as long as I had sunk in several hours into this project, I might as well publicize the results.


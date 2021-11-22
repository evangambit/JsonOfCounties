
Weather data is measured at physical stations, which do not have a 1-to-1 mapping to counties.  Instead we use latitudes/longitudes to find the station that is nearest to a county's center.

We don't average over counties contained by a county, because I'm not really sure how to handle some geometric oddities (e.g. missing a chunk in their middle or counties that include islands).

In the NOAA dataset
- Temperature is in tenths-of-Fahrenheits
- Percipitation is in hundredths of inches
- Snow is in tenths of inches

We convert these to Fahrenheights and inches respectively.

# Files:

NOAA's README ("noaa-readme.txt"):

https://www1.ncdc.noaa.gov/pub/data/normals/1981-2010/readme.txt

Station locations:

https://www1.ncdc.noaa.gov/pub/data/normals/1981-2010/source-datasets/ghcnd-stations.txt

Annual snow

ftp://ftp.ncdc.noaa.gov/pub/data/normals/1981-2010/products/precipitation/ann-snow-normal.txt

Annual percipitation

ftp://ftp.ncdc.noaa.gov/pub/data/normals/1981-2010/products/precipitation/ann-prcp-normal.txt

Avg temperature:

ftp://ftp.ncdc.noaa.gov/pub/data/normals/1981-2010/products/temperature/ann-tavg-normal.txt

Monthly Average Temperature:

ftp://ftp.ncdc.noaa.gov/pub/data/normals/1981-2010/products/temperature/mly-tavg-normal.txt


import os, requests, pandas, time

"""
https://www.countyhealthrankings.org/sites/default/files/media/document/2021%20County%20Health%20Rankings%20Alabama%20Data%20-%20v1.xlsx



https://www.countyhealthrankings.org/sites/default/files/media/document/2021%20County%20Health%20Rankings%20Alabama%20Data%20-%20v1_0.xlsx
"""

def download_state(state):
  fn = os.path.join('generated', 'state-health', state + '.xlsx')
  if not os.path.exists(fn):
    time.sleep(1)
    url = f"https://www.countyhealthrankings.org/sites/default/files/media/document/2021%20County%20Health%20Rankings%20{state.replace(' ', '%20')}%20Data%20-%20v1.xlsx"
    if state in ['Alabama', 'Mississippi', 'Tennessee', 'Virginia', 'Nevada']:
      url = f"https://www.countyhealthrankings.org/sites/default/files/media/document/2021%20County%20Health%20Rankings%20{state.replace(' ', '%20')}%20Data%20-%20v1_0.xlsx"
    print(url)
    r = requests.get(url, allow_redirects=True)
    with open(fn, 'wb+') as f:
      f.write(r.content)

states = [
  "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming",
]

datadir = os.path.join('generated', 'state-health')
if not os.path.exists(datadir):
  os.mkdir(datadir)
for state in states:
  download_state(state)

header = [
  'FIPS',
  r'% Fair or Poor Health',
  'Average Number of Physically Unhealthy Days',
  'Average Number of Mentally Unhealthy Days',
  r'% Low birthweight',
  r'% Smokers',
  r'% Adults with Obesity',
  'Food Environment Index',
  r'% Physically Inactive',
  r'% Excessive Drinking',
  '# Alcohol-Impaired Driving Deaths',
  'Teen Birth Rate',
  r'% Uninsured',
  r'% With Annual Mammogram',
  r'% Vaccinated',
  r'% Children in Poverty',
  '80th Percentile Income',
  '20th Percentile Income',
  r'% Children in Single-Parent Households',
  'Violent Crime Rate',
  'Average Daily PM2.5',
  r'% Severe Housing Problems',
  r'% Drive Alone to Work',
  r'% Long Commute - Drives Alone',
]

rows = []

def foo(x):
  if type(x) is str and ':' in x:
    a, b = x.split(':')
    assert b == '1', x
    return float(a)
  return x

for fn in os.listdir(datadir):
  print(fn)
  a = pandas.ExcelFile(os.path.join(datadir, fn))
  s = a.parse('Ranked Measure Data')

  fips = s['Unnamed: 0']
  A = [
    s['Unnamed: 0'],
    s['Poor or fair health'],
    s['Poor physical health days'],
    s['Poor mental health days'],
    s['Unnamed: 42'],
    s['Adult smoking'],
    s['Adult obesity'],
    s['Food environment index'],
    s['Physical inactivity'],
    s['Excessive drinking'],
    s['Alcohol-impaired driving deaths'],
    s['Teen births'],
    s['Unnamed: 110'],
    s['Mammography screening'],
    s['Flu vaccinations'],
    s['Children in poverty'],
    s['Income inequality'],
    s['Unnamed: 173'],
    s['Unnamed: 178'],
    s['Unnamed: 186'],
    s['Air pollution - particulate matter'],
    s['Severe housing problems'],
    s['Driving alone to work'],
    s['Unnamed: 245'],
  ]

  B = [a[0] for a in A]
  assert B == header

  for i in range(1, len(A[0])):
    rows.append([foo(a[i]) for a in A])

body = '\n'.join([','.join(str(x) for x in row) for row in rows])
with open(os.path.join('generated', 'county-health.csv'), 'w+') as f:
  f.write(','.join(header) + '\n' + body)



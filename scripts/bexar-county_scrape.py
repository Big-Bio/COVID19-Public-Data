import requests
import os, sys, time
import parse_data_utils
from datetime import datetime

# ===========================================
# Grab update time information
# ===========================================

# Page only tells "Updated daily at 7 PM [CDT]"
# as of 4/19/2020. Thus, just take current date.
# Make sure to run this between 5 and 11:59 PM
# for Pacific time!

# Need date in format MM/DD/YYYY
date_parts = str(datetime.date(datetime.now())).split('-')
date = date_parts[1] + '/' + date_parts[2] + '/' + date_parts[0]

# ===========================================
# Grab current zip code-case counts data
# ===========================================

san_antonio_url = "https://services.arcgis.com/g1fRTDLeMgspWrYp/arcgis/rest/services/vBexarCountyZipCodes_EnrichClip/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&outFields=*&orderByFields=ZIP_CODE%20asc"
san_antonio_case_field = u'CasesP100000'

response = requests.get(san_antonio_url) # REST API query

try:
	all_zip_json = response.json()[u'features']
except:
	sys.exit("ERROR: JSON response does not have 'features' field. URL may be incorrect or field names may have changed.")

# Loading population data to estimate case counts
san_antonio_pop_data_path = os.path.abspath("./san_antonio_pop_by_zip.csv")
san_antonio_pop_data_file = open(san_antonio_pop_data_path, 'r')
san_antonio_pop_data_file.readline() # Get rid of header

zip_code_pop_dict = {}
for line in san_antonio_pop_data_file:
	values = line.strip().split(',')
	zip_code, pop = values[1], values[7]
	zip_code_pop_dict[zip_code] = int(pop)

san_antonio_pop_data_file.close()

zip_codes = [] # List of zip codes
case_counts = [] # List of case counts

for zip_json in all_zip_json:
	cases_per_100k = zip_json[u'attributes'][san_antonio_case_field]
	zip_code = zip_json[u'attributes'][u'ZIP_CODE']	
	if zip_code in zip_code_pop_dict:
		case_count = round(cases_per_100k*zip_code_pop_dict[zip_code]/100000)
		case_counts.append(case_count)
		zip_codes.append(zip_code)

# ===========================================
# Store previous data in dictionary
# ===========================================

us_cases_rel_scripts_path = os.path.abspath("../processed_data/cases/US") # Path to data relative to scripts
prev_data_fpath = "%s/bexar-county_cases.csv" % us_cases_rel_scripts_path
prev_data_file = open(prev_data_fpath, 'r')
header = prev_data_file.readline().strip().split(',')

# IMPORTANT: Only append new data if date isn't already there
quoted_date = parse_data_utils.date_string_to_quoted(date)

if quoted_date in header:
	prev_data_file.close()
	sys.exit("This date has already been updated. May need to check if multiple updates were made in the same day.")

data = {} # Keys are zip codes, values are lists of case counts

for row in prev_data_file:
	values = row.strip().split(',')
	zip_code = values[0]
	case_counts_prev = values[1:]
	data[zip_code] = case_counts_prev

prev_data_file.close()

# ===========================================
# Add today's data and overwrite .csv
# ===========================================

num_dates = len(header) - 1 # Excludes today

for zip_code, case_count in zip(zip_codes, case_counts):
	quoted_zip_code = '"%s"' % zip_code
	if quoted_zip_code in data:
		data[quoted_zip_code].append(str(case_count))
	else: # New zip code
		data[quoted_zip_code] = ['NA'] * (num_dates)
		data[quoted_zip_code].append(str(case_count))

# Missing zip codes
for zip_code in data:
	if len(data[zip_code]) < (num_dates + 1):
		data[zip_code].append("NA")

# Make sure everything has the same length
# (There might be duplicates!)
for zip_code in data:
	if len(data[zip_code]) != (num_dates + 1):
		sys.exit("ERROR: Inconsistency in number of data points for zip code %s" % zip_code)

# Overwrite csv
data_file = open(prev_data_fpath, 'w')

header.append(quoted_date)
data_file.write(','.join(header) + "\n")
sorted_zip_codes = sorted(data.keys())

for zip_code in sorted_zip_codes:
	data_file.write('%s,' % zip_code)
	data_file.write(','.join(data[zip_code]) + "\n")

data_file.close()

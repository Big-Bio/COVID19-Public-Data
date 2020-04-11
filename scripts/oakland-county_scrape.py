import requests
import os, sys, time
import parse_data_utils
# PhantomJS executable must be in PATH
from selenium import webdriver

# ===========================================
# Grab update time information
# ===========================================

oakland_base_url = "https://oakgov.maps.arcgis.com/apps/opsdashboard/index.html#/462154e746b04af884c548111eccee73"

driver = webdriver.PhantomJS()
driver.get(oakland_base_url)
time.sleep(5) # Wait for PhantomJS to do its thing
update_element = driver.find_element_by_xpath("//*[contains(text(), 'Updated')]")
update_string = update_element.text

# Parse: assume form like 'Updated 4/8/2020, 2:15 PM"
date = update_string.split(' ')[1].strip(',')
time = update_string.split(' ')[2:3]

# ===========================================
# Grab current zip code-case counts data
# ===========================================

oakland_data_url = "https://services1.arcgis.com/GE4Idg9FL97XBa3P/arcgis/rest/services/COVID19_Cases_by_Zip_Code_Total_Population/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&outFields=*&orderByFields=Join_Zip_Code%20asc"
oakland_case_field = u'Join_Count'

response = requests.get(oakland_data_url) # REST API query

try:
	all_zip_json = response.json()[u'features']
except:
	sys.exit("ERROR: JSON response does not have 'features' field. URL may be incorrect or field names may have changed.")

zip_codes = [] # List of zip codes
case_counts = [] # List of case counts

for zip_json in all_zip_json:
	case_count = zip_json[u'attributes'][oakland_case_field]
	zip_code = zip_json[u'attributes'][u'Join_Zip_Code']	
	case_counts.append(case_count)
	zip_codes.append(zip_code)

# ===========================================
# Store previous data in dictionary
# ===========================================

us_cases_rel_scripts_path = os.path.abspath("../processed_data/cases/US") # Path to data relative to scripts
prev_data_fpath = "%s/oakland-county_cases.csv" % us_cases_rel_scripts_path
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

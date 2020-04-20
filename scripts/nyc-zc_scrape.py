import requests
import os, sys, time
import parse_data_utils
from datetime import datetime

# ===========================================
# Grab update time information
# ===========================================

# So far, commits have been made to test-by-zcta.csv
# around 1-6 PM EST. So run after 3 PM (and before
# 11:59 PM) on the day of for PST.

# Need date in format MM/DD/YYYY
date_parts = str(datetime.date(datetime.now())).split('-')
date = date_parts[1] + '/' + date_parts[2] + '/' + date_parts[0]

# ===========================================
# Grab current zip code-case counts data
# ===========================================

nyc_data_url = "https://raw.githubusercontent.com/nychealth/coronavirus-data/master/tests-by-zcta.csv"

response = requests.get(nyc_data_url).text # Grabs raw csv

zip_codes = [] # List of zip codes
case_counts = [] # List of case counts

for line in response.split('\n')[1:]:
	zip_code, case_count, _, _ = line.strip().split(',')
	case_counts.append(str(int(case_count)))
	zip_codes.append(zip_code)

# ===========================================
# Store previous data in dictionary
# ===========================================

us_cases_rel_scripts_path = os.path.abspath("../processed_data/cases/US") # Path to data relative to scripts
prev_data_fpath = "%s/nyc-zc_cases.csv" % us_cases_rel_scripts_path
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
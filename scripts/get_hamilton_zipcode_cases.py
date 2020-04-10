import requests
import os
import sys
import time
import csv
from selenium import webdriver
from collections import defaultdict

hamilton_cases_zipcode_url = 'https://www.hamiltoncountyhealth.org/covid19/'
# chrome driver should be in the PATH
driver = webdriver.Chrome()
driver.get(hamilton_cases_zipcode_url)
time.sleep(3)

update_info = driver.find_element_by_xpath("//*[contains(text(), 'Updated')]").text
update_date = update_info.strip('.').split()[-1]
update_date_element = update_date.split('/')
processed_update_date_element = []
for e in update_date_element:
    if len(e) == 1:
        e = '0' + e
    processed_update_date_element.append(e)
processed_update_date = '/'.join(processed_update_date_element)

# odd elements are zip codes, even elements are cases
cases_zipcode = {}
raw_cases_zipcode = driver.find_element_by_tag_name('table').text.split()[4:]
for i in range(0, len(raw_cases_zipcode), 2):
    cases_zipcode[raw_cases_zipcode[i]] = raw_cases_zipcode[i+1]

# combine with old data
orig_data_file = '../processed_data/cases/US/hamilton-county_cases.csv'
data = defaultdict(list)
with open(orig_data_file, 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for row in reader:
        if row[0] == '':
            data['date'] += row[1:]
        else:
            data[row[0]] += row[1:]

if processed_update_date in data['date']:
    sys.exit('Data of this date has been updated.')

for zipcode, cases in cases_zipcode.items():
    data[zipcode].append(cases)
data['date'].append(processed_update_date)
for key in data:
    if len(data[key]) != len(data['date']):
        data[key].append('NA')

with open(orig_data_file, 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    writer.writerow([''] + data['date'])
    for key in sorted(data.keys()):
        if key != 'date':
            writer.writerow([key] + data[key])


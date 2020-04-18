import requests
import os, sys, time, re
import parse_data_utils
from datetime import datetime
"""
This script scrapes data from Esri ArcGIS to get COVID-19 counts by zip code. It
is currently written to take counts for Sarpy County, NE; Douglas County, NE;
and Spokane County, WA.
Code for the script is based off of oakland-county_scrape.py (by Daisy Chen) and
is meant to be run with Python 3.

Note: this script can be easily extended to scrape data for another county using
ArcGIS by adding an entry to csv_names, overview_urls, data_urls, zip_fields,
and case_fields at the bottom of this script.
"""


def get_update_date(overview_url):
    """Fetches the last update date for the data.
    
    Args:
        overview_url: The url from which to grab the date.
    Returns:
        A string of the form mm/dd/yyyy.
    """
    response = requests.get(overview_url)

    #response HTML will hold date in the form:
    #<b>Last Edit Date:</b> 4/16/2020 10:31:29 PM<br/>
    regex = '<b>Last Edit Date:</b>(.*)<br/>'
    pattern = re.compile(regex)
    res = re.search(pattern, response.text)
    utc_str_time = res.group(1).strip()
    utc_time = datetime.strptime(utc_str_time, '%m/%d/%Y %I:%M:%S %p')

    # Convert time to local time
    now_timestamp = time.time()
    timezone_offset = datetime.fromtimestamp(now_timestamp) - \
        datetime.utcfromtimestamp(now_timestamp)
    local_time = utc_time + timezone_offset

    date = local_time.strftime('%m/%d/%Y')
    #local_time = local_time.strftime('%H:%M:%S')
    return date


def get_case_counts(data_url, case_field, zip_field):
    """Fetches the case counts for each zip code.
    
    Args:
        data_url: The url from which to grab the data.
        case_field: The field name for the xml element holding the case counts.
        zip_field: The field name for the xml element holding the zip codes.
        
    Returns:
        zips, cases
        where zips is a list of zip codes and cases is a list of the corresponding case counts.
    """
    response = requests.get(data_url)

    try:
        all_zips = response.json()[u'features']
    except:
        sys.exit("ERROR: could not extract 'features' field from JSON.")

    zips = []  # List of zip codes
    cases = []  # List of case counts

    for zip in all_zips:
        case_count = zip[u'attributes'][case_field]
        zip_code = zip[u'attributes'][zip_field]
        if zip_code != None:
            cases.append(case_count)
            zips.append(zip_code)

    return zips, cases


def write_data(file_path, date, zips, cases):
    """Writes or appends the data to a csv. Rows are zip codes and columns are dates.
    
    Args:
        file_path: The path to the csv to write/append to.
        date: The date we should add data to.
        zip: List of zip codes to be updated.
        cases: List of cases corresponding to the given list of zip codes and the given date.
    """
    # Fetch given csv and store in a dict.
    new_data = {}  # Keys are zip codes, values are lists of case counts
    dates = [""]
    # IMPORTANT: Only append new data if date isn't already there
    quoted_date = parse_data_utils.date_string_to_quoted(date)
    overwrite = False

    try:
        read_csv = open(file_path, 'r')
        dates = read_csv.readline().strip().split(',')
        if quoted_date in dates:
            overwrite = True
            print("WARNING: data has already been updated today... "
                  "overwriting data for today with recently fetched data.")
        # Fill in new_data with old data from the csv.
        for row in read_csv:
            values = row.strip().split(',')
            zip_code = values[0]
            old_cases = values[1:]
            if overwrite:
                old_cases = values[1:-1]
            new_data[zip_code] = old_cases
        read_csv.close()
    except IOError:
        print("Creating csv file at %s" % file_path)

    num_dates = len(dates) - 1  # Excluding today
    if overwrite:
        num_dates = num_dates - 1

    # Fill in new_data with today's data.
    for zip_code, case_count in zip(zips, cases):
        quoted_zip_code = '"%s"' % zip_code
        if quoted_zip_code in new_data:
            new_data[quoted_zip_code].append(str(case_count))
        else:  # New zip code
            new_data[quoted_zip_code] = ['NA'] * (num_dates)
            new_data[quoted_zip_code].append(str(case_count))

    expected_entries = num_dates + 1

    # Handle missing zip codes
    for zip_code in new_data:
        if len(new_data[zip_code]) < expected_entries:
            new_data[zip_code].append("NA")

    # Make sure everything has the same length
    # (There might be duplicates!)
    for zip_code in new_data:
        if len(new_data[zip_code]) != expected_entries:
            print(new_data[zip_code])
            print(expected_entries)
            sys.exit(
                "ERROR: Inconsistency in number of data points for zip code %s."
                " Data failed to update." % zip_code)

    # Overwrite csv
    write_csv = open(file_path, 'w+')

    if not overwrite:
        dates.append(quoted_date)
    write_csv.write(','.join(dates) + "\n")
    sorted_zip_codes = sorted(new_data.keys())

    for zip_code in sorted_zip_codes:
        write_csv.write('%s,' % zip_code)
        write_csv.write(','.join(new_data[zip_code]) + "\n")

    write_csv.close()


if __name__ == "__main__":
    # Filenames for the CSVs
    csv_names = [
        "sarpy-nebraska_cases.csv", "douglas-nebraska_cases.csv",
        "spokane-washington_cases.csv"
    ]

    # URLs with ArcGIS feature layer description through which to scrape the
    # last edit date
    overview_urls = [
        "https://services.arcgis.com/OiG7dbwhQEWoy77N/arcgis/rest/services/SarpyCassCOVID_View/FeatureServer/0",
        "https://services.arcgis.com/pDAi2YK0L0QxVJHj/arcgis/rest/services/COVID19_Cases_by_ZIP_(View)/FeatureServer/0",
        "https://services7.arcgis.com/Zrf5IrTQfEv8XhMg/arcgis/rest/services/Covid_Cases_by_Zipcode/FeatureServer/0"
    ]

    # URLs with REST API call to query for case counts
    data_urls = [
        "https://services.arcgis.com/OiG7dbwhQEWoy77N/arcgis/rest/services/SarpyCassCOVID_View/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&outFields=ZipCode,Cases&orderByFields=ZipCode",
        "https://services.arcgis.com/pDAi2YK0L0QxVJHj/arcgis/rest/services/COVID19_Cases_by_ZIP_(View)/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&outFields=*",
        "https://services7.arcgis.com/Zrf5IrTQfEv8XhMg/arcgis/rest/services/Covid_Cases_by_Zipcode/FeatureServer/0/query?f=json&where=ZIP_RATE%3E0&returnGeometry=false&outFields=ZCTA5CE10,N&orderByFields=ZCTA5CE10"
    ]

    # Name of the field storing the zip codes in the data_url's response
    zip_fields = [u'ZipCode', u'ZipCode', 'ZCTA5CE10']

    # Name of the field storing the case counts in the data_url's response
    case_fields = [u'Cases', u'Cases', u'N']

    cases_rel_path = os.path.abspath("../processed_data/cases/US")

    for i in range(0, len(csv_names)):
        csv_name = csv_names[i]
        overview_url = overview_urls[i]
        data_url = data_urls[i]
        case_field = case_fields[i]
        zip_field = zip_fields[i]

        file_path = "%s/%s" % (cases_rel_path, csv_name)

        date = get_update_date(overview_url)
        zips, cases = get_case_counts(data_url, case_field, zip_field)
        write_data(file_path, date, zips, cases)

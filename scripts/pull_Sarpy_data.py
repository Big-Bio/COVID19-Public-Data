import requests
import os, sys, time
import parse_data_utils
"""
This script scrapes data from ArcGIS to get COVID-19 counts by zip code. It is
currently written to take counts for Sarpy County in NE (dashboard can be found
at https://covid19.dogis.org/app/90ea18d2368e43d495255a13b6989ae8).
Code for the script is based off of oakland-county_scrape.py (by Daisy Chen).
"""


def get_update_date(date_query_url, time_field):
    """Fetches the last update date for the data.
    
    Args:
        date_query_url: The url from which to grab the date.
        time_field: The field name for the xml element holding the time.
    Returns:
        A string of the form mm/dd/yyyy.
    """
    response = requests.get(date_query_url)

    try:
        features = response.json()[u'features']
    except:
        sys.exit("ERROR: could not extract 'features' field from JSON.")

    epoch_time = features[0][u'attributes'][
        time_field]  # the epoch time of the last time the data was updated in ms
    date = time.strftime('%m/%d/%Y', time.localtime(epoch_time / 1000.0))
    #local_time = time.strftime('%H:%M:%S', time.localtime(epoch_time/1000.0))
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
            print(
                "WARNING: data has already been updated today... "
                "overwriting data for today with recently fetched data."
            )
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

    num_dates = 0  # Excludes today
    if (len(dates) > 1):
        num_dates = len(
            dates) - 2  # List of dates begins with an empty string.

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
                " Data failed to update."
                % zip_code)

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
    date_query_url = "https://services.arcgis.com/OiG7dbwhQEWoy77N/arcgis/rest/services/SarpyCassCOVID_View/FeatureServer/1/query?f=json&where=1%3D1&returnGeometry=false&outFields=EditDate&orderByFields=EditDate%20desc&maxFeatures=1"
    data_url = "https://services.arcgis.com/OiG7dbwhQEWoy77N/arcgis/rest/services/SarpyCassCOVID_View/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&outFields=ZipCode,Cases&orderByFields=ZipCode"

    time_field = u'EditDate'
    case_field = u'Cases'
    zip_field = u'ZipCode'

    csv_name = "sarpy_cases.csv"
    cases_rel_path = os.path.abspath("../processed_data/cases/US")
    file_path = "%s/%s" % (cases_rel_path, csv_name)

    date = get_update_date(date_query_url, time_field)
    zips, cases = get_case_counts(data_url, case_field, zip_field)
    write_data(file_path, date, zips, cases)

#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import logging
import numpy as np
import os
import pandas as pd
import sys
import urllib2

BORO = 'boro'
BORO_DATA_URL = \
    'https://raw.githubusercontent.com/nychealth/coronavirus-data/master/boro.csv'

logging.basicConfig(filename='log/boroProcess.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                    )
logger = logging.getLogger()


def fetchBoroDataFromURL(input_directory):
    """Fetches boro data from BORO_DATA_URL and write to boro_data/.

    Fetches latest boro data provided by BORO_DATA_URL and saves it to 
    boro_data/ with filename 'boro${month}${day}${year}'. For example, 
    if the program is executed on April 8, 2020, then the filename 
    will be 'boro04082020'.

    Args:
        None

    Returns:
        None

    """
    now = datetime.datetime.now()
    try:
        filename = input_directory + 'boro' + now.strftime('%m%d%Y')
        response = urllib2.urlopen(BORO_DATA_URL)
        content = response.read()
        with open(filename, 'w') as file:
            file.write(content)
        logger.info('Sucess: Fetch boro data for day: ' + now.strftime('%m%d%Y'))
    except:
        logger.error('Fail: Can not fetch boro data for day: ' + now.strftime('%m%d%Y'))


def fetchFilenamesFromDirectory(directory):
    """Fetches the name of all files in the specified directory.

    Args:
        directory: str, the path to the specified directory

    Returns:
        list of str, the name of all files in the specified directory

    """
    return os.listdir(directory)


def fetchTimeFromFilename(filename):
    """Fetches the name from the given filename and formats it.

    For example, given the filename 'boro04082020', this function
    will return '4/8/20'.

    Args:
        filename: str, the filename of boro data e.g. 'boro04082020'

    Returns:
        str, the formatted time, e.g. '4/8/20'

    """
    month = str(int(filename[4:6]))
    day = str(int(filename[6:8]))
    year = filename[10:12]
    return month + '/' + day + '/' + year


def processBoroData(input_directory):
    """Fetches all the boro data from the specified directory.

    Args:
        input_directory: str, the directory which saves all boro data

    Returns:
        boro_data: dict. The key is the day and the value is a 
                         dictionary, say D, for the corresponding day.
                         The key of D is the region, the value of D
                         is the number of cases. If there is a missing
                         value, the value of D will be 'NA'.
        regions: dict, the key is the name of the region.
                   
    """
    list_of_filenames = fetchFilenamesFromDirectory(input_directory)
    boro_data = {}
    regions = {}
    for filename in list_of_filenames:
        if filename[:4] != BORO or len(filename) != 12:
            continue
        logger.info('Fetch Boro data from file: ' + input_directory
                    + filename)
        try:
            daily_data = pd.read_csv(input_directory
                    + filename).applymap(str)
        except:
            logger.error('Fail to fetch Boro data from file: '
                         + input_directory + filename)
        time = fetchTimeFromFilename(filename)

        for (_, row) in daily_data.iterrows():
            region = row['BOROUGH_GROUP'].lower()
            if region == 'bronx':
                region = 'the bronx'
            if time not in boro_data:
                boro_data[time] = {}
            boro_data[time][region] = row['COVID_CASE_COUNT']
            if region not in regions:
                regions[region] = True
    return (boro_data, regions)


def getDays():
    """Fetches all days from Jan 22, 2020 to the execution day.

    Args:
        None

    Returns:
        list of str, all the formatted time between Jan 22, 2020
                     to the execution day. An example of list element
                     is '4/8/20'.

    """
    now = datetime.datetime.now()
    start_date = datetime.date(2020, 1, 22)
    end_date = datetime.date(now.year, now.month, now.day)
    delta = datetime.timedelta(days=1)
    days = []

    while start_date <= end_date:
        time = str(start_date.month) + '/' + str(start_date.day) + '/' \
            + str(start_date.year)[-2:]
        start_date += delta
        days.append(time)
    return days


def format_boro_data(boro_data, regions, output_filename):
    """Formats boro data and output to a csv file.

    Args:
        boro_data: dict. The key is the day and the value is a 
                         dictionary, say D, for the corresponding day.
                         The key of D is the region, the value of D
                         is the number of cases. If there is a missing
                         value, the value of D will be 'NA'.
        regions: dict, the key is the name of the region.
        output_filename: str, the path to the output csv file

    Returns:
        None

    """
    days = getDays()
    formatted_data = {'': days}

    for region in regions:
        region_cases = []
        for day in days:
            if day not in boro_data or region not in boro_data[day] \
                or boro_data[day][region] == np.NaN:
                region_cases.append('NA')
            else:
                region_cases.append(boro_data[day][region])
        formatted_data[region] = region_cases
    pd.DataFrame(formatted_data).T.to_csv(output_filename,
            header=False, index=True)


def main():
    # Get input directory and output filename from command line arguments
    if len(sys.argv) != 3:
        print('Incorrect number of arguments. '  \
              'Usage: python boroProcess.py '  \
              '${input_directory} ${output_fliename}')
    input_directory = sys.argv[1]
    output_filename = sys.argv[2]

    # Fetch boro data from the gien URL
    fetchBoroDataFromURL(input_directory)

    # Process/format boro data and output to a csv file
    (boro_data, regions) = processBoroData(input_directory)
    format_boro_data(boro_data, regions, output_filename)


if __name__ == '__main__':
    main()

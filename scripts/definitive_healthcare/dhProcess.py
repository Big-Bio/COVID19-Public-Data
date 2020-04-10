#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import numpy as np
import os
import pandas as pd
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import utils

DEFINITIVE_HEALTHCARE_PREFIX = \
    'Definitive_Healthcare__USA_Hospital_Beds_'

logging.basicConfig(filename='log/dhProcess.log', level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                    )
logger = logging.getLogger()


def fetchTimeFromFilename(filename):
    """Fetches the name from the given filename and formats it.

    For example, given the filename 
    'Definitive_Healthcare__USA_Hospital_Beds_04-07-2020.csv'
    this function will return '4/7/20'.

    Args:
        filename: str, the filename of definitive healthcare data

    Returns:
        str, the formatted time

    """

    month = str(int(filename[41:43]))
    day = str(int(filename[44:46]))
    year = filename[49:51]
    return month + '/' + day + '/' + year


def readDataFromDirectory(input_directory):
    """Fetches all the definitive healthcare data from the specified directory.

    Args:
        input_directory: str, the directory which saves all data

    Returns:
        beds_utilization_summary: dict. The key is the day and the value 
                         is a dictionary, say D, for the corresponding day.
                         The key of D is the hospital name, the value of D
                         is the bed utilization for that hospital. If there 
                         is a missing value, the value of D will be 'NA'.
        ventilator_usage_summary: dict. The key is the day and the value 
                         is a dictionary, say D, for the corresponding day.
                         The key of D is the hospital name, the value of D
                         is the ventilator usage for that hospital. If there 
                         is a missing value, the value of D will be 'NA'.
        hospital_names: dict, the key is the name of the hospital.

    """

    list_of_filenames = \
        utils.fetchFilenamesFromDirectory(input_directory)
    beds_utilization_summary = {}
    ventilator_usage_summary = {}
    hospital_names = {}

    for filename in list_of_filenames:
        if filename[:41] != DEFINITIVE_HEALTHCARE_PREFIX \
            or len(filename) != 55:
            continue
        logger.info('Fetch definitive healthcare data from file: '
                    + input_directory + filename)
        try:
            daily_data = pd.read_csv(input_directory
                    + filename).applymap(str)
        except:
            logger.error('Fail to fetch definitive healthcare data from file: '
                          + input_directory + filename)
        time = fetchTimeFromFilename(filename)

        for (_, row) in daily_data.iterrows():
            hospital_name = row['HOSPITAL_NAME']
            bed_utilization = row['BED_UTILIZATION']
            avg_ventilator_usage = row['AVG_VENTILATOR_USAGE']
            if hospital_name not in hospital_names:
                hospital_names[hospital_name] = True
            if time not in beds_utilization_summary:
                beds_utilization_summary[time] = {}
            if time not in ventilator_usage_summary:
                ventilator_usage_summary[time] = {}
            if bed_utilization != 'nan':
                beds_utilization_summary[time][hospital_name] = \
                    bed_utilization
            if avg_ventilator_usage != 'nan':
                ventilator_usage_summary[time][hospital_name] = \
                    avg_ventilator_usage

    return (beds_utilization_summary, ventilator_usage_summary,
            hospital_names)


def format_output_data(
    beds_utilization_summary,
    ventilator_usage_summary,
    hospital_names,
    output_directory,
    ):
    """Formats definitive healthcare data and output to a csv file.

    Args:
        beds_utilization_summary: dict. The key is the day and the value 
                         is a dictionary, say D, for the corresponding day.
                         The key of D is the hospital name, the value of D
                         is the bed utilization for that hospital. If there 
                         is a missing value, the value of D will be 'NA'.
        ventilator_usage_summary: dict. The key is the day and the value 
                         is a dictionary, say D, for the corresponding day.
                         The key of D is the hospital name, the value of D
                         is the ventilator usage for that hospital. If there 
                         is a missing value, the value of D will be 'NA'.
        hospital_names: dict, the key is the name of the hospital.
        output_directory: str, the path to the output directory. 
                          e.g. processed_data/

    Returns:
        None

    """

    days = utils.getDays()
    formatted_beds_data = {'': days}
    formatted_ventilators_data = {'': days}

    for hospital_name in hospital_names:
        beds_data = []
        ventilators_data = []
        for day in days:
            if day not in beds_utilization_summary or hospital_name \
                not in beds_utilization_summary[day] \
                or beds_utilization_summary[day][hospital_name] \
                == np.NaN \
                or len(beds_utilization_summary[day][hospital_name]) \
                == 0:
                beds_data.append('NA')
            else:
                beds_data.append(beds_utilization_summary[day][hospital_name])

            if day not in ventilator_usage_summary or hospital_name \
                not in ventilator_usage_summary[day] \
                or ventilator_usage_summary[day][hospital_name] \
                == np.NaN \
                or len(ventilator_usage_summary[day][hospital_name]) \
                == 0:
                ventilators_data.append('NA')
            else:
                ventilators_data.append(ventilator_usage_summary[day][hospital_name])

        formatted_beds_data[hospital_name] = beds_data
        formatted_ventilators_data[hospital_name] = ventilators_data

    pd.DataFrame(formatted_beds_data).T.to_csv(output_directory
            + 'beds/US/us-hospital_beds.csv', header=False, index=True)
    logger.info('Sucess: write processed data to ' + output_directory
                + 'beds/US/us-hospital_beds.csv')
    pd.DataFrame(formatted_ventilators_data).T.to_csv(output_directory
            + 'ventilators/US/us-hospital_ventilators.csv',
            header=False, index=True)
    logger.info('Sucess: write processed data to ' + output_directory
                + 'ventilators/US/us-hospital_ventilators.csv')


def main():
    # Get input directory and output directory from command line arguments
    if len(sys.argv) != 3:
        print('Incorrect number of arguments. ' \
            'Usage: python dhProcess.py ${input_directory} ${output_directory}')
    input_directory = sys.argv[1]
    output_directory = sys.argv[2]

    # Process/format definitive healthcare from the given URL
    (beds_utilization_summary, ventilator_usage_summary,
     hospital_names) = readDataFromDirectory(input_directory)
    format_output_data(beds_utilization_summary,
                       ventilator_usage_summary, hospital_names,
                       output_directory)


if __name__ == '__main__':
    main()

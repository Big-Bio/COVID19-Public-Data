#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import os


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


def fetchFilenamesFromDirectory(directory):
    """Fetches the name of all files in the specified directory.

    Args:
        directory: str, the path to the specified directory

    Returns:
        list of str, the name of all files in the specified directory

    """
    return os.listdir(directory)
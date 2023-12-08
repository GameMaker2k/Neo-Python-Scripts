#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

'''
    This program is free software; you can redistribute it and/or modify
    it under the terms of the Revised BSD License.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    Revised BSD License for more details.

    Copyright 2018-2019 Game Maker 2k - https://github.com/GameMaker2k
    Copyright 2018-2019 Kazuki Przyborowski - https://github.com/KazukiPrzyborowski

    $FileInfo: pycal.py - Last Update: 3/6/2021 Ver. 1.2.0 RC 1 - Author: joshuatp $
'''

from __future__ import print_function;
import sys, argparse;
from datetime import date;

__program_name__ = "PyCal";
__project__ = __program_name__;
__project_url__ = "https://github.com/GameMaker2k/Neo-Python-Scripts";
__version_info__ = (1, 2, 0, "RC 1", 1);
__version_date_info__ = (2019, 3, 6, "RC 1", 1);
__version_date__ = str(__version_date_info__[0])+"."+str(__version_date_info__[1]).zfill(2)+"."+str(__version_date_info__[2]).zfill(2);
if(__version_info__[4]!=None):
 __version_date_plusrc__ = __version_date__+"-"+str(__version_date_info__[4]);
if(__version_info__[4]==None):
 __version_date_plusrc__ = __version_date__;
if(__version_info__[3]!=None):
 __version__ = str(__version_info__[0])+"."+str(__version_info__[1])+"."+str(__version_info__[2])+" "+str(__version_info__[3]);
if(__version_info__[3]==None):
 __version__ = str(__version_info__[0])+"."+str(__version_info__[1])+"."+str(__version_info__[2]);

def isleapyear_gregorian(year):
    if year % 400 == 0:
        return True
    if year % 100 == 0:
        return False
    return year % 4 == 0

def isleapyear_julian(year):
    return year % 4 == 0

def isleapyear_revised_julian(year):
    if year % 900 in [200, 600]:
        return True
    if year % 100 == 0:
        return False
    return year % 4 == 0

def isleapyear(year, gregorian=True, revised=False):
    if gregorian:
        return isleapyear_gregorian(year)
    if revised:
        return isleapyear_revised_julian(year)
    return isleapyear_julian(year)

def get_month_start(current_day, current_month, current_year, time_info, normal_start=True, gregorian=True, newcode=True):
    current_century = (current_year - 1) // 100 + 1
    current_year_short = abs(current_year) % 100
    year_code = (current_year_short + current_year_short // 4) % 7
    month_code = time_info['monthinfo']['month_code_list'][current_month]
    # Calculate century code
    if newcode:
        century_code = [0, 6, 4, 2][current_century % 4]
    else:
        century_code = [0, 6, 4, 2][(current_century - 1) % 4]
    # Adjust for non-Gregorian calendars
    if not gregorian:
        century_code = (18 - century_code) % 7
    # Check for leap year adjustment
    is_leap = isleapyear(current_year, gregorian)
    leap_year_adjustment = (current_month == 0 or current_month == 1) and is_leap
    # Calculate the day
    ret_val = (year_code + month_code + century_code + current_day - leap_year_adjustment) % 7
    # Adjust if the week does not start on Sunday
    if not normal_start:
        ret_val = (ret_val - 1) % 7
    return ret_val

def count_number_of_days(current_month, current_year, time_info, gregorian=True, revised=False):
    day_count = 0
    is_previous_year_leap = isleapyear(current_year - 1, gregorian, revised)
    # Choose the correct list of days per month based on leap year or not
    if is_previous_year_leap:
        days_per_month = time_info['monthinfo']['numberofdays']['leapyear']
    else:
        days_per_month = time_info['monthinfo']['numberofdays']['normalyear']
    # Sum the days for the months from the current month to the end of the year
    for month in range(current_month, len(days_per_month)):
        day_count += days_per_month[month]
    return day_count

def get_week_number(current_day, current_month, current_year, time_info, normal_start=True, gregorian=True, revised=False):
    # Count the number of days in the year up to the current month
    total_days = count_number_of_days(current_month - 1, current_year, time_info, gregorian, revised)
    # Add the days of the current month
    total_days += current_day
    # Calculate the week number
    week_number = total_days // 7
    # If the week does not start on Sunday, adjust the week number
    if not normal_start:
        week_number += 1
    return week_number

def print_month(current_month, current_year, time_info, normal_start=True, gregorian=True, revised=False, week_number=False, print_year=False):
    if current_year < 0:
        current_year = 0
    # Determine the start of the month and January
    month_start = get_month_start(1, current_month, current_year, time_info, normal_start, gregorian, revised)
    jan_month_start = get_month_start(1, 1, current_year, time_info, normal_start, gregorian, revised)
    # Print the month header
    month_name = time_info['monthinfo']['longname'][current_month]
    header = f"{month_name} {current_year}" if print_year else month_name
    print(header.center(26 if week_number else 20))
    # Print day names
    day_names = time_info['dayinfo']['shortname'] if normal_start else time_info['dayinfo']['altshortname']
    day_name_line = " ".join(day_names)
    if week_number:
        day_name_line = "   " + day_name_line
    print(day_name_line)
    # Calculate days in the month and total days till the current month
    is_leap = isleapyear(current_year, gregorian, revised)
    days_in_month = (time_info['monthinfo']['numberofdays']['leapyear' if is_leap else 'normalyear'])[current_month]
    total_days_till_month = count_number_of_days(current_month, current_year, time_info, gregorian, revised)
    # Print the days
    day_count = 1
    for week in range(6):  # Assuming maximum 6 weeks in a month
        if week_number:
            week_num = (total_days_till_month + day_count) // 7 + 1
            print(f"{week_num:2}", end=" ")
        for day in range(7):
            if week == 0 and day < month_start:
                print("   ", end="")  # Print spaces for days before month starts
            elif day_count <= days_in_month:
                print(f"{day_count:2}", end=" ")
                day_count += 1
            else:
                print("   ", end="")  # Print spaces for days after month ends
        print()  # New line at the end of the week
    return True

def print_multiple_months(current_month, current_year, before, after, time_info, normal_start=True, gregorian=True, revised=False, week_number=False):
    # Calculate the start month and year
    start_month = (current_month - before) % 12
    start_year = current_year - ((current_month - before) // 12)
    # Calculate the end month and year
    end_month = (current_month + after) % 12
    end_year = current_year + ((current_month + after) // 12)
    while True:
        # Print the year header for January or the first month in the sequence
        if start_month == 0:
            print(str(start_year).center(20))
        # Print the month
        print_month(start_month, start_year, time_info, normal_start, gregorian, revised, week_number, False)
        # Move to the next month
        start_month = (start_month + 1) % 12
        if start_month == 0:
            start_year += 1
        # Check if the end has been reached
        if (start_year > end_year) or (start_year == end_year and start_month > end_month):
            break
    return True

def print_year(current_year, time_info, normal_start=True, gregorian=True, revised=False, week_number=False):
    # Ensure year is non-negative
    current_year = max(current_year, 0)
    # Print the year header
    print(str(current_year).center(20))
    # Print each month of the year
    for current_month in range(time_info['monthinfo']['numberofmonths']):
        print_month(current_month, current_year, time_info, normal_start, gregorian, revised, week_number, False)
    return True

def print_multiple_year(current_year, before, after, time_info, normal_start=True, gregorian=True, revised=False, week_number=False):
    start_year = current_year - before
    end_year = current_year + after
    for year in range(start_year, end_year + 1):
        print_year(year, time_info, normal_start, gregorian, revised, week_number)
    return True

yearinfo = {
 'dayinfo' : {
  'numberofdays': 7,
  'longname': { 0: "Sunday", 1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday", 6: "Saturday" },
  'shortname': { 0: "Su", 1: "Mo", 2: "Tu", 3: "We", 4: "Th", 5: "Fr", 6: "Sa" },
  'shortnamealt': { 0: "Sun", 1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri", 6: "Sat" },
  'altlongname': { 0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday" },
  'altshortname': { 0: "Mo", 1: "Tu", 2: "We", 3: "Th", 4: "Fr", 5: "Sa", 6: "Su" },
  'altshortnamealt': { 0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun" }
 },
 'monthinfo' : {
  'numberofmonths': 12,
  'longname': { 0: "January", 1: "February", 2: "March", 3: "April", 4: "May", 5: "June", 6: "July", 7: "August", 8: "September", 9: "October", 10: "November", 11: "December", 12: "Test" },
  'shortname': { 0: "Jan", 1: "Feb", 2: "Mar", 3: "Apr", 4: "May", 5: "Jun", 6: "Jul", 7: "Aug", 8: "Sept", 9: "Oct", 10: "Nov", 11: "Dec", 11: "Tes" },
  'month_code_list': { 0: 0, 1: 3, 2: 3, 3: 6, 4: 1, 5: 4, 6: 6, 7: 2, 8: 5, 9: 0, 10: 3, 11: 5 },
  'numberofdays': { 
   'normalyear': { 0: 31, 1: 28, 2: 31, 3: 30, 4: 31, 5: 30, 6: 31, 7: 31, 8: 30, 9: 31, 10: 30, 11: 31 },
   'leapyear': { 0: 31, 1: 29, 2: 31, 3: 30, 4: 31, 5: 30, 6: 31, 7: 31, 8: 30, 9: 31, 10: 30, 11: 31 },
   'ordinaldayny': { 0: 0, 1: 31, 2: 59, 3: 90, 4: 120, 5: 151, 6: 181, 7: 212, 8: 243, 9: 273, 10: 304, 11: 334 },
   'ordinaldayly': { 0: 0, 1: 31, 2: 60, 3: 91, 4: 121, 5: 152, 6: 182, 7: 213, 8: 244, 9: 274, 10: 305, 11: 335 },
  }
 }
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(conflict_handler="resolve", add_help=True)
    parser.add_argument("-y", "--year", type=int, default=date.today().year, help="Enter year")
    parser.add_argument("-m", "--month", type=int, default=date.today().month, help="Enter month or -1 for whole year")
    parser.add_argument("-3", "--three", action="store_true", help="Show num months starting with date's month")
    parser.add_argument("-o", "--monday", action="store_false", help="Start weeks on Monday")
    parser.add_argument("-j", "--julian", action="store_false", help="Use the Julian calendar")
    parser.add_argument("-r", "--revised", action="store_true", help="Use revised Julian calendar")
    parser.add_argument("-w", "--week", action="store_true", help="Show US or ISO-8601 week numbers")
    parser.add_argument("-v", "--version", action="version", version=__program_name__ + " " + __version__)
    getargs = parser.parse_args()

    current_month = getargs.month if getargs.month > 0 else date.today().month - 1
    current_year = getargs.year if getargs.year > 0 else date.today().year

    if getargs.month < 0:
        print_year(current_year, yearinfo, getargs.monday, getargs.julian, getargs.revised, getargs.week)
    elif getargs.three:
        print_multiple_months(current_month, current_year, 1, 1, yearinfo, getargs.monday, getargs.julian, getargs.revised, getargs.week)
    else:
        print_month(current_month, current_year, yearinfo, getargs.monday, getargs.julian, getargs.revised, getargs.week, True)

        print_multiple_months(current_month, current_year, 1, 1, yearinfo, getargs.monday, getargs.julian, getargs.revised, getargs.week)
    else:
        print_month(current_month, current_year, yearinfo, getargs.monday, getargs.julian, getargs.revised, getargs.week, True)

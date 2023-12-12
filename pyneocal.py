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

class CalendarInfo:
    DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    MONTH_DAYS_NORMAL = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    MONTH_DAYS_LEAP = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    @staticmethod
    def short_name(names):
        return [name[:3] for name in names]

    @staticmethod
    def cumulative_days(year_type):
        days = CalendarInfo.MONTH_DAYS_LEAP if year_type == 'leap' else CalendarInfo.MONTH_DAYS_NORMAL
        return [sum(days[:i]) for i in range(1, len(days) + 1)]

    @staticmethod
    def is_leap_year_gregorian(year):
        return (year % 4 == 0) and (year % 100 != 0 or year % 400 == 0)

    @staticmethod
    def is_leap_year_julian(year):
        return year % 4 == 0

    @staticmethod
    def is_leap_year_revised_julian(year):
        return year % 900 in [200, 600] or year % 100 != 0

    @staticmethod
    def is_leap_year(year, calendar='gregorian'):
        if calendar == 'gregorian':
            return CalendarInfo.is_leap_year_gregorian(year)
        elif calendar == 'julian':
            return CalendarInfo.is_leap_year_julian(year)
        elif calendar == 'revised_julian':
            return CalendarInfo.is_leap_year_revised_julian(year)
        else:
            raise ValueError(f"Unknown calendar system: {calendar}")

def get_month_start(current_day, current_month, current_year, normal_start=True, calendar='gregorian'):
    current_century = (current_year - 1) // 100 + 1
    current_year_short = abs(current_year) % 100
    year_code = (current_year_short + (current_year_short // 4)) % 7

    # Use CalendarInfo.MONTH_CODE_LIST instead of time_info
    month_code = CalendarInfo.MONTH_CODE_LIST[current_month]

    # Use CalendarInfo.CENTURY_CODE_LIST for century code
    century_code = CalendarInfo.CENTURY_CODE_LIST[current_century % 4]

    # Adjust for Julian calendar
    if calendar != 'gregorian':
        century_code = (18 - century_code) % 7

    # Check leap year using CalendarInfo class
    is_leap = CalendarInfo.is_leap_year(current_year, calendar)
    leap_year_adjustment = 1 if (current_month < 2 and is_leap) else 0

    ret_val = (year_code + month_code + century_code + current_day - leap_year_adjustment) % 7

    # Adjust for week start
    if not normal_start and ret_val > 0:
        ret_val -= 1
    elif not normal_start:
        ret_val = 6

    return ret_val

def count_number_of_days(current_month, current_year, calendar='gregorian'):
    # Determine if the year is a leap year
    is_leap = CalendarInfo.is_leap_year(current_year, calendar)

    # Select the appropriate month day list based on leap year status
    month_days = CalendarInfo.MONTH_DAYS_LEAP if is_leap else CalendarInfo.MONTH_DAYS_NORMAL

    # Sum the number of days from the current month to the end of the year
    daycount = sum(month_days[current_month:])

    return daycount

def get_week_number(current_date, current_month, current_year, normal_start=True, calendar='gregorian'):
    # Determine if the year is a leap year
    is_leap = CalendarInfo.is_leap_year(current_year, calendar)

    # Select the appropriate month day list based on leap year status
    month_days = CalendarInfo.MONTH_DAYS_LEAP if is_leap else CalendarInfo.MONTH_DAYS_NORMAL

    # Calculate the day of the year for the current date
    day_of_year = sum(month_days[:current_month]) + current_date

    # Adjust for week start
    if not normal_start:
        day_of_year += 1

    # Calculate the week number
    week_number = (day_of_year - 1) // 7 + 1

    return week_number

def print_month(current_month, current_year, normal_start=True, calendar='gregorian', week_number=False, print_year=False):
    is_leap = CalendarInfo.is_leap_year(current_year, calendar)
    month_days = CalendarInfo.MONTH_DAYS_LEAP if is_leap else CalendarInfo.MONTH_DAYS_NORMAL

    # Header for month and year
    month_name = CalendarInfo.MONTHS[current_month]
    header = f"{month_name} {current_year}" if print_year else month_name
    print(header.center(26 if week_number else 20))

    # Weekday names
    day_names = CalendarInfo.short_name(CalendarInfo.DAYS if normal_start else CalendarInfo.DAYS[1:] + [CalendarInfo.DAYS[0]])
    print(" ".join(day_names).center(26 if week_number else 20))

    # Calculate starting position of the first day of the month
    month_start = get_month_start(1, current_month, current_year, normal_start, calendar)

    # Print the calendar days
    day_of_week = 0
    if week_number:
        week_num = 1
        print(f"{week_num:2}", end=" ")
    for _ in range(month_start):
        print("   ", end="")
        day_of_week += 1
    for day in range(1, month_days[current_month] + 1):
        print(f"{day:2}", end=" ")
        day_of_week = (day_of_week + 1) % 7
        if day_of_week == 0:
            if week_number:
                week_num += 1
                print(f"\n{week_num:2}", end=" ")
            else:
                print()

def print_multiple_months(current_month, current_year, before, after, normal_start=True, gregorian=True, week_number=False):
    start_month = (current_month - before) % 12
    start_year = current_year + ((current_month - before) // 12)
    end_month = (current_month + after) % 12
    end_year = current_year + ((current_month + after) // 12)

    while True:
        print_month(start_month, start_year, normal_start, gregorian, week_number, print_year=True)
        start_month = (start_month + 1) % 12
        if start_month == 0:
            start_year += 1
        if (start_month > end_month and start_year == end_year) or (start_year > end_year):
            break

def print_year(current_year, normal_start=True, calendar='gregorian', week_number=False):
    if current_year < 0:
        current_year = 0

    print(str(current_year).center(20))

    for current_month in range(12):  # Assuming 12 months in a year
        print_month(current_month, current_year, normal_start, calendar, week_number, False)

def print_multiple_year(current_year, before, after, normal_start=True, calendar='gregorian', week_number=False):
    start_year = current_year - before
    end_year = current_year + after

    for year in range(start_year, end_year + 1):
        print_year(year, normal_start, calendar, week_number)

def main():
    parser = argparse.ArgumentParser(description="Calendar Display Tool")
    parser.add_argument("-y", "--year", type=int, default=date.today().year, help="Enter year (default: current year)")
    parser.add_argument("-m", "--month", type=int, default=date.today().month, help="Enter month (1-12) or -1 for the whole year")
    parser.add_argument("-t", "--three", action="store_true", help="Show three months starting from the specified month")
    parser.add_argument("-o", "--monday", action="store_true", help="Start weeks on Monday")
    parser.add_argument("-j", "--julian", action="store_true", help="Use the Julian calendar")
    parser.add_argument("-r", "--revised", action="store_true", help="Use the Revised Julian calendar")
    parser.add_argument("-w", "--week", action="store_true", help="Show week numbers")
    args = parser.parse_args()

    # Adjust the calendar and week start settings
    calendar = 'julian' if args.julian else 'revised_julian' if args.revised else 'gregorian'
    normal_start = not args.monday

    if args.month == -1:
        print_year(args.year, normal_start, calendar, args.week)
    elif args.three:
        print_multiple_months(args.month - 1, args.year, 1, 1, normal_start, calendar, args.week)
    else:
        print_month(args.month - 1, args.year, normal_start, calendar, args.week, True)

if __name__ == "__main__":
    main()

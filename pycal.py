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

    $FileInfo: pycal.py - Last Update: 1/3/2019 Ver. 1.0.0 RC 1 - Author: joshuatp $
'''

from __future__ import print_function;
import sys, argparse;
from datetime import date;

__program_name__ = "PyCal";
__project__ = __program_name__;
__project_url__ = "https://gist.github.com/KazukiPrzyborowski";
__version_info__ = (1, 0, 0, "RC 1", 1);
__version_date_info__ = (2019, 1, 3, "RC 1", 1);
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
 if(year % 4):
  return False;
 elif(not year % 100):
  return True;
 elif(not year % 400):
  return False;
 else:
  return True;
 return True;

def isleapyear_julian(year):
 if(year % 4):
  return False;
 else:
  return True;
 return True;

def isleapyear_revised_julian(year):
 if(int(year % 900)==200 or int(year % 900)==600):
  return True;
 elif(not year % 100):
  return False;
 else:
  return True;
 return True;

def isleapyear(year, gregorian=True, revised=False):
 if(gregorian is True):
  return isleapyear_gregorian(year);
 else:
  if(revised):
   return isleapyear_revised_julian(year);
  else:
   return isleapyear_julian(year);
 return True;

def get_month_start(current_day, current_month, current_year, normal_start=True, gregorian=True):
 current_century = (current_year - 1) // 100 + 1;
 current_year_short = abs(current_year) % 100;
 year_code = (current_year_short + (current_year_short / 4)) % 7;
 month_code_list = { 0: 0, 1: 3, 2: 3, 3: 6, 4: 1, 5: 4, 6: 6, 7: 2, 8: 5, 9: 0, 10: 3, 11: 5 }
 month_code = month_code_list[current_month];
 century_code_list = [0, 6, 4, 2];
 count_century = 0;
 count_century_list = 0;
 while(count_century<=current_century):
  if(count_century==current_century):
   century_code = century_code_list[count_century_list];
  if(count_century_list>2):
   count_century_list = 0;
  else:
   count_century_list += 1;
  count_century += 1;
 if(gregorian is False):
  century_code = (18 - century_code) % 7;
 if((current_month==0 or current_month==1) and (isleapyear(current_year, True) and gregorian is True)):
  ret_val = int((year_code + month_code + century_code + current_day - 1) % 7);
  if(normal_start is False):
   if(ret_val > 0):
    ret_val -= 1;
   else:
    ret_val = 6;
  return ret_val;
 elif((current_month==0 or current_month==1) and (isleapyear(current_year, False) and gregorian is False)):
  ret_val = int((year_code + month_code + century_code + current_day - 1) % 7);
  if(normal_start is False):
   if(ret_val > 0):
    ret_val -= 1;
   else:
    ret_val = 6;
  return ret_val;
 else:
  ret_val = int((year_code + month_code + century_code + current_day) % 7);
  if(normal_start is False):
   if(ret_val > 0):
    ret_val -= 1;
   else:
    ret_val = 6;
  return ret_val;

def print_month(current_month, current_year, time_info, normal_start=True, gregorian=True, revised=False, print_year=False):
 if(current_year<0):
  current_year = 0;
 month_start = get_month_start(1, current_month, current_year, normal_start, gregorian);
 if(print_year is False):
  print("");
  print(time_info['monthinfo']['longname'][current_month].center(20));
 else:
  print(str(time_info['monthinfo']['longname'][current_month]+" "+str(current_year)).center(20));
 numcountdays = 0;
 while(numcountdays<7):
  if(normal_start is True):
   print(time_info['dayinfo']['shortname'][numcountdays], end=" ");
  else:
   print(time_info['dayinfo']['altshortname'][numcountdays], end=" ");
  numcountdays += 1;
 else:
  numcountdays = 0;
  print("");
 dacount = 0;
 if(isleapyear(current_year, True) and gregorian is True):
  numberofdays = 0;
  if(current_month>0):
   mocount = 0;
   while(mocount<current_month):
    dacount = dacount + time_info['monthinfo']['numberofdays']['leapyear'][mocount];
    mocount = mocount + 1;
  numdaysformonth = time_info['monthinfo']['numberofdays']['leapyear'][current_month];
 elif(isleapyear(current_year, False, revised) and gregorian is False):
  numberofdays = 0;
  if(current_month>0):
   mocount = 0;
   while(mocount<current_month):
    dacount = dacount + time_info['monthinfo']['numberofdays']['leapyear'][mocount];
    mocount = mocount + 1;
  numdaysformonth = time_info['monthinfo']['numberofdays']['leapyear'][current_month];
 else:
  numberofdays = 0;
  if(current_month>0):
   mocount = 0;
   while(mocount<current_month):
    dacount = dacount + time_info['monthinfo']['numberofdays']['normalyear'][mocount];
    mocount = mocount + 1;
  numdaysformonth = time_info['monthinfo']['numberofdays']['normalyear'][current_month];
 numcountdaysformonth = 1;
 while(numcountdaysformonth <= numdaysformonth):
  numcountdays = 0;
  while(numcountdays<month_start and numcountdaysformonth==1):
   print("  ", end=" ");
   numcountdays += 1;
  numweek = 0;
  while(numcountdays<7 and numcountdaysformonth <= numdaysformonth):
   weeknum = int(dacount / 7) + 1;
   if(numcountdays==0 or numcountdaysformonth==1):
    print("("+str(weeknum)+")", numcountdaysformonth, end=" " );
   dacount = dacount + 1;
   print(str(numcountdaysformonth).rjust(2), end=" ");
   numcountdays += 1;
   numcountdaysformonth += 1;
  else:
   numcountdays = 0;
   print("");
 return True;

def print_year(current_year, time_info, normal_start=True, gregorian=True, revised=False):
 if(current_year<0):
  current_year = 0;
 print(str(current_year).center(20));
 current_month = 0;
 while(current_month<time_info['monthinfo']['numberofmonths']):
  print_month(current_month, current_year, time_info, normal_start, gregorian, revised, False);
  current_month += 1;
 return True;

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
  'longname': { 0: "January", 1: "February", 2: "March", 3: "April", 4: "May", 5: "June", 6: "July", 7: "August", 8: "September", 9: "October", 10: "November", 11: "December" },
  'shortname': { 0: "Jan", 1: "Feb", 2: "Mar", 3: "Apr", 4: "May", 5: "Jun", 6: "Jul", 7: "Aug", 8: "Sept", 9: "Oct", 10: "Nov", 11: "Dec" },
  'numberofdays': { 
   'normalyear': { 0: 31, 1: 28, 2: 31, 3: 30, 4: 31, 5: 30, 6: 31, 7: 31, 8: 30, 9: 31, 10: 30, 11: 31 },
   'leapyear': { 0: 31, 1: 29, 2: 31, 3: 30, 4: 31, 5: 30, 6: 31, 7: 31, 8: 30, 9: 31, 10: 30, 11: 31 }
  }
 }
}

if(__name__ == "__main__"):
 parser = argparse.ArgumentParser(conflict_handler = "resolve", add_help = True);
 parser.add_argument("-y", "--year", type=int, default = date.today().year, help = "enter year");
 parser.add_argument("-m", "--month", type=int, default = (date.today().month-1), help = "enter month or -1 for whole year");
 parser.add_argument("-o", "--monday", action="store_false", help = "start weeks on monday");
 parser.add_argument("-j", "--julian", action="store_false", help = "use the julian calendar");
 parser.add_argument("-r", "--revised", action="store_true", help = "use revised julian calendar");
 parser.add_argument("-v", "--version", action = "version", version = __program_name__+" "+__version__);
 getargs = parser.parse_args();

if(__name__ == "__main__"):
 if(getargs.month==0 and getargs.year<=0):
  print_month((date.today().month-1), date.today().year, yearinfo, getargs.monday, getargs.julian, getargs.revised, True);
 elif(getargs.month==0 and getargs.year>0):
  print_month((date.today().month-1), getargs.year, yearinfo, getargs.monday, getargs.julian, getargs.revised, True);
 elif(getargs.month<0 and getargs.year<=0):
  print_year(date.today().year, yearinfo, getargs.monday, getargs.julian, getargs.revised);
 elif(getargs.month<0 and getargs.year>0):
  print_year(getargs.year, yearinfo, getargs.monday, getargs.julian, getargs.revised);
 elif(getargs.month>0 and getargs.year<=0):
  print_month((getargs.month-1), date.today().year, yearinfo, getargs.monday, getargs.julian, getargs.revised, True);
 elif(getargs.month>0 and getargs.year>0):
  print_month((getargs.month-1), getargs.year, yearinfo, getargs.monday, getargs.julian, getargs.revised, True);
 else:
  print_year(getargs.year, yearinfo, getargs.monday, getargs.julian, getargs.revised);

#!/usr/bin/env python

'''
    This program is free software; you can redistribute it and/or modify
    it under the terms of the Revised BSD License.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    Revised BSD License for more details.

    Copyright 2019 Game Maker 2k - https://github.com/GameMaker2k
    Copyright 2019 Kazuki Przyborowski - https://github.com/KazukiPrzyborowski

    $FileInfo: drnim.py - Last Update: 5/9/2019 Ver. 1.0.0 RC 1 - Author: kazuki $
'''

from __future__ import print_function;

__program_name__ = "Dr. Nim";
__project__ = __program_name__;
__project_url__ = "https://gist.github.com/KazukiPrzyborowski";
__version_info__ = (1, 0, 0, "RC 1", 1);
__version_date_info__ = (2019, 5, 9, "RC 1", 1);
__version_date__ = str(__version_date_info__[0])+"."+str(__version_date_info__[1]).zfill(2)+"."+str(__version_date_info__[2]).zfill(2);
if(__version_info__[4]!=None):
 __version_date_plusrc__ = __version_date__+"-"+str(__version_date_info__[4]);
if(__version_info__[4]==None):
 __version_date_plusrc__ = __version_date__;
if(__version_info__[3]!=None):
 __version__ = str(__version_info__[0])+"."+str(__version_info__[1])+"."+str(__version_info__[2])+" "+str(__version_info__[3]);
if(__version_info__[3]==None):
 __version__ = str(__version_info__[0])+"."+str(__version_info__[1])+"."+str(__version_info__[2]);

'''
    https://en.wikipedia.org/wiki/Dr._Nim
    https://en.wikipedia.org/wiki/Nim
'''

def dr_nim(gofirst=True, yourturn=1):
 if(gofirst is True):
  return dr_nim_second(4, yourturn);
 else:
  return dr_nim_first(5, yourturn);

def dr_nim_second(coins=4, yourturn=1):
 if(yourturn<1 or yourturn>3):
  return False;
 else:
  if(yourturn==1):
   youtook = "one coin";
   nimtook = "three coins";
   nimturn = 3;
  elif(yourturn==2):
   youtook = "two coins";
   nimtook = "two coins";
   nimturn = 2;
  else:
   youtook = "three coins";
   nimtook = "one coin";
   nimturn = 3;
  print("You took "+youtook+".");
  coins -= yourturn;
  print("Dr Nim took "+nimtook+".");
  coins -= nimturn;
  print("You lose.");
  print("Dr Nim wins.");
  if(coins<1):
   return True;
  else:
   return False;

def dr_nim_first(coins=5, yourturn=1):
 if(yourturn<1 or yourturn>7):
  return False;
 else:
  if(coins==5):
   print("Dr Nim took one coin.");
   coins -= 1;
  if(coins==6):
   print("Dr Nim took two coins.");
   coins -= 2;
  if(coins==7):
   print("Dr Nim took three coins.");
   coins -= 3;
  return dr_nim_second(coins, yourturn);

numcount = 4;
numstart = 1;
while(numstart<numcount):
 print(dr_nim(False, numstart));
 print("");
 print(dr_nim(True, numstart));
 if(numstart<(numcount - 1)):
  print("");
 numstart += 1;

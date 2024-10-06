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

from __future__ import print_function

__program_name__ = "Dr. Nim"
__project__ = __program_name__
__project_url__ = "https://gist.github.com/KazukiPrzyborowski"
__version_info__ = (1, 0, 0, "RC 1", 1)
__version_date_info__ = (2019, 5, 9, "RC 1", 1)
__version_date__ = str(__version_date_info__[0])+"."+str(__version_date_info__[
    1]).zfill(2)+"."+str(__version_date_info__[2]).zfill(2)
if(__version_info__[4] != None):
    __version_date_plusrc__ = __version_date__ + \
        "-"+str(__version_date_info__[4])
if(__version_info__[4] == None):
    __version_date_plusrc__ = __version_date__
if(__version_info__[3] != None):
    __version__ = str(__version_info__[0])+"."+str(__version_info__[1])+"."+str(
        __version_info__[2])+" "+str(__version_info__[3])
if(__version_info__[3] == None):
    __version__ = str(
        __version_info__[0])+"."+str(__version_info__[1])+"."+str(__version_info__[2])

'''
    https://en.wikipedia.org/wiki/Dr._Nim
    https://en.wikipedia.org/wiki/Nim
'''


def dr_nim(gofirst=True, coins=12, yourturn=1):
    if(gofirst is True):
        return dr_nim_second(coins, yourturn)
    else:
        return dr_nim_first(coins, yourturn)


def dr_nim_second(coins=4, yourturn=1):
    scoin = coins
    if(yourturn < 1 or yourturn > 3):
        return False
    else:
        drnimwon = True
        while(True):
            if(coins > 0):
                if(yourturn == 1 or coins == 1):
                    youtook = "one coin"
                    if(coins == 1):
                        yourturn = 1
                elif(yourturn == 2 or coins == 2):
                    youtook = "two coins"
                    if(coins == 2):
                        yourturn = 2
                else:
                    youtook = "three coins"
                    if(coins == 3):
                        yourturn = 3
                print("You took "+youtook+".")
                coins -= yourturn
            if(coins <= 0):
                drnimwon = False
                break
            nimtook = ""
            if(coins < 8 and coins != 4):
                if(coins == 3):
                    nimtook = "three coins"
                    nimturn = 3
                elif(coins == 5):
                    nimtook = "one coin"
                    nimturn = 1
                elif(coins == 6):
                    nimtook = "two coin"
                    nimturn = 2
                elif(coins == 7):
                    nimtook = "three coins"
                    nimturn = 3
                elif(coins == 2):
                    nimtook = "two coins"
                    nimturn = 2
                elif(coins == 1):
                    nimtook = "one coin"
                    nimturn = 1
            elif(int(coins % 3) == 0):
                nimtook = "three coins"
                nimturn = 3
            elif(int(coins % 3) == 1):
                nimtook = "two coins"
                nimturn = 2
            elif(int(coins % 3) == 2):
                nimtook = "one coin"
                nimturn = 1
            if(nimtook != ""):
                print("Dr Nim took "+nimtook+".")
                coins -= nimturn
            if(coins <= 0):
                drnimwon = True
                break
        if(drnimwon):
            print("You lose.")
            print("Dr Nim wins.")
        else:
            print("You won.")
            print("Dr Nim lose.")
        if(drnimwon):
            return False
        else:
            return True


def dr_nim_first(coins=5, yourturn=1):
    if(yourturn < 1 or yourturn > 7):
        return False
    else:
        nimtook = ""
        if(coins < 8 and coins != 4):
            if(coins == 3):
                nimtook = "three coins"
                nimturn = 3
            elif(coins == 5):
                nimtook = "one coin"
                nimturn = 1
            elif(coins == 6):
                nimtook = "two coin"
                nimturn = 2
            elif(coins == 7):
                nimtook = "three coins"
                nimturn = 3
            elif(coins == 2):
                nimtook = "two coins"
                nimturn = 2
            elif(coins == 1):
                nimtook = "one coin"
                nimturn = 1
        elif(int(coins % 3) == 0):
            nimtook = "three coins"
            nimturn = 3
        elif(int(coins % 3) == 1):
            nimtook = "two coins"
            nimturn = 2
        elif(int(coins % 3) == 2):
            nimtook = "one coin"
            nimturn = 1
        if(nimtook != ""):
            print("Dr Nim took "+nimtook+".")
            coins -= nimturn
        return dr_nim_second(coins, yourturn)


numcount = 12
numstart = 1
yourwins = 0
yourloses = 0
while(numstart < numcount):
    drnimf = dr_nim(False, numstart, 3)
    print(drnimf)
    if(drnimf):
        yourwins = yourwins + 1
    else:
        yourloses = yourloses + 1
    print("")
    drnims = dr_nim(True, numstart, 3)
    print(drnims)
    if(drnims):
        yourwins = yourwins + 1
    else:
        yourloses = yourloses + 1
    if(numstart < (numcount - 1)):
        print("")
    numstart += 1
print("")
print("Your Loses: "+str(yourloses))
print("Your Wins: "+str(yourwins))

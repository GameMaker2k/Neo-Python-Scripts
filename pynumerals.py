#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    This program is free software; you can redistribute it and/or modify
    it under the terms of the Revised BSD License.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    Revised BSD License for more details.
    Copyright 2019 Game Maker 2k - https://github.com/GameMaker2k
    Copyright 2019 Kazuki Przyborowski - https://github.com/KazukiPrzyborowski
    $FileInfo: pynumerals.py - Last Update: 12/22/2021 Ver. 0.0.1 RC 1 - Author: kazukisp $
'''

western_arabic = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];
eastern_arabic = ['٠' ,'١' ,'٢' ,'٣' ,'٤' ,'٥' ,'٦' ,'٧' ,'٨' ,'٩'];
persian = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];
urdu = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];

western_to_eastern = {}
wcount = 0;
wcountmax = 10;
while(wcount<wcountmax):
 western_to_eastern.update( { western_arabic[wcount] : eastern_arabic[wcount] } );
 wcount += 1;

western_to_persian = {}
wcount = 0;
wcountmax = 10;
while(wcount<wcountmax):
 western_to_persian.update( { western_arabic[wcount] : persian[wcount] } );
 wcount += 1;

western_to_urdu = {}
wcount = 0;
wcountmax = 10;
while(wcount<wcountmax):
 western_to_urdu.update( { western_arabic[wcount] : urdu[wcount] } );
 wcount += 1;

eastern_to_western = {}
ecount = 0;
ecountmax = 10;
while(ecount<ecountmax):
 eastern_to_western.update( { eastern_arabic[ecount] : western_arabic[ecount] } );
 ecount += 1;

eastern_to_persian = {}
ecount = 0;
ecountmax = 10;
while(ecount<ecountmax):
 eastern_to_persian.update( { eastern_arabic[ecount] : persian[ecount] } );
 ecount += 1;

eastern_to_urdu = {}
ecount = 0;
ecountmax = 10;
while(ecount<ecountmax):
 eastern_to_urdu.update( { eastern_arabic[ecount] : urdu[ecount] } );
 ecount += 1;

persian_to_western = {}
pcount = 0;
pcountmax = 10;
while(pcount<pcountmax):
 persian_to_western.update( { persian[pcount] : western_arabic[pcount] } );
 pcount += 1;

persian_to_eastern = {}
pcount = 0;
pcountmax = 10;
while(pcount<pcountmax):
 persian_to_eastern.update( { persian[pcount] : eastern_arabic[pcount] } );
 pcount += 1;

persian_to_urdu = {}
pcount = 0;
pcountmax = 10;
while(pcount<pcountmax):
 persian_to_urdu.update( { persian[pcount] : urdu[pcount] } );
 pcount += 1;

urdu_to_western = {}
ucount = 0;
ucountmax = 10;
while(ucount<ucountmax):
 urdu_to_western.update( { urdu[ucount] : western_arabic[ucount] } );
 ucount += 1;

urdu_to_eastern = {}
ucount = 0;
ucountmax = 10;
while(ucount<ucountmax):
 urdu_to_eastern.update( { urdu[ucount] : eastern_arabic[ucount] } );
 ucount += 1;

urdu_to_persian = {}
ucount = 0;
ucountmax = 10;
while(ucount<ucountmax):
 urdu_to_persian.update( { urdu[ucount] : persian[ucount] } );
 wcount += 1;

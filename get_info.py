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

def get_info(invar):
 inname = invar.__name__;
 intype = type(invar).__name__;
 indec = id(invar);
 inhex = hex(indec);
 try:
  inprempath = invar.__package__;
 except AttributeError:
  inprempath = invar.__module__;
 inprempath = globals()[inprempath]
 inmpath = getattr(inprempath, "__file__");
 outstr = "<"+intype+" '"+inname+"' from '"+inm+"'>";
 return outstr;

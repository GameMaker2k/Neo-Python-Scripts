#!/usr/bin/env python

'''
    This program is free software; you can redistribute it and/or modify
    it under the terms of the Revised BSD License.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    Revised BSD License for more details.

    Copyright 2016 Game Maker 2k - https://github.com/GameMaker2k
    Copyright 2016 Joshua Przyborowski - https://github.com/JoshuaPrzyborowski

    $FileInfo: pyeleccalc.py - Last Update: 02/02/2016 Ver. 0.0.1 RC 2 - Author: joshuatp $
'''

def GetWattsDC(amps, volts):
 watts = float(float(amps) * float(volts));
 return float(watts);

def GetWattageDC(amps, volts):
 watts = float(float(amps) * float(volts));
 return float(watts);

def GetAmpsDC(watts, volts):
 amps = float(float(watts) / float(volts));
 return float(amps);

def GetAmperageDC(watts, volts):
 amps = float(float(watts) / float(volts));
 return float(amps);

def GetVoltsDC(watts, amps):
 volts = float(float(watts) / float(amps));
 return float(volts);

def GetVoltageDC(watts, amps):
 volts = float(float(watts) / float(amps));
 return float(volts);

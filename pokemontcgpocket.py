'''
    This program is free software; you can redistribute it and/or modify
    it under the terms of the Revised BSD License.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    Revised BSD License for more details.
    Copyright 2016 Game Maker 2k - https://github.com/GameMaker2k
    Copyright 2016 Joshua Przyborowski - https://github.com/JoshuaPrzyborowski
    $FileInfo: pokemontcgpocket.py - Last Update: 08/15/2017 Ver. 0.0.1 RC 2 - Author: joshuatp $
'''

from __future__ import division, print_function
import math

# Random Pokemon TCG Pocket Calc App

def CalcPokemonTCGBattlePotins(twins, tpoints, mdamage, multi=3, divi=3):
    calcfist = (twins * multi) -  tpoints
    calcsecond = math.ceil(tpoints / divi) - twins
    calcfinal = (calcfist + calcsecond) + mdamage
    return calcfinal

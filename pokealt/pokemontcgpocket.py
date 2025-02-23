#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
import argparse
import math

def CalcPokemonTCGBattlePoints(twins, tpoints, mdamage, plevel=1, multi=3, divi=3):
    """
    Calculate a final battle score based on:
      - twins  = total wins
      - tpoints = total points
      - mdamage = max damage
      - plevel  = player level (1 to 50)
      - multi   = multiplier for wins (default=3)
      - divi    = divisor for points (default=3)
    """
    # Ensure player level is capped at 50
    plevel = min(plevel, 50)

    # Original calculation
    calcfist = (twins * multi) - tpoints
    calcsecond = math.ceil(tpoints / divi) - twins
    calcfinal = calcfist + calcsecond + mdamage

    # Add a flat bonus: 0.5 points per level
    calcfinal += (plevel * 0.5)

    return calcfinal

def main():
    parser = argparse.ArgumentParser(description="Calculate Pokemon TCG Battle Points.")
    parser.add_argument("twins", type=int, help="Total wins")
    parser.add_argument("tpoints", type=int, help="Total points")
    parser.add_argument("mdamage", type=int, help="Max damage dealt")
    parser.add_argument("--plevel", type=int, default=1,
                        help="Player level (default: 1, capped at 50)")
    parser.add_argument("--multi", type=int, default=3,
                        help="Multiplier for wins (default: 3)")
    parser.add_argument("--divi", type=int, default=3,
                        help="Divisor for points (default: 3)")
    
    args = parser.parse_args()
    
    # Call our updated function
    result = CalcPokemonTCGBattlePoints(
        twins=args.twins,
        tpoints=args.tpoints,
        mdamage=args.mdamage,
        plevel=args.plevel,
        multi=args.multi,
        divi=args.divi
    )

    print("Calculated Pokemon TCG Battle Points: {0}".format(result))

if __name__ == "__main__":
    main()

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

def CalcPokemonTCGBattlePotins(twins, tpoints, mdamage, multi=3, divi=3):
    calcfist = (twins * multi) - tpoints
    calcsecond = math.ceil(tpoints / divi) - twins
    calcfinal = (calcfist + calcsecond) + mdamage
    return calcfinal

def main():
    parser = argparse.ArgumentParser(description="Calculate Pokemon TCG Battle Points.")
    parser.add_argument("twins", type=int, help="Total wins")
    parser.add_argument("tpoints", type=int, help="Total points")
    parser.add_argument("mdamage", type=int, help="Max damage dealt")
    parser.add_argument("--multi", type=int, default=3, help="Multiplier (default: 3)")
    parser.add_argument("--divi", type=int, default=3, help="Divisor (default: 3)")
    
    args = parser.parse_args()
    
    result = CalcPokemonTCGBattlePotins(args.twins, args.tpoints, args.mdamage, args.multi, args.divi)
    print(f"Calculated Pokemon TCG Battle Points: {result}")

if __name__ == "__main__":
    main()

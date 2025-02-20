#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This program is free software; you can redistribute it and/or modify
it under the terms of the Revised BSD License.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the Revised BSD License for more details.
"""

def calc_pokemon_tcg_battle_points(twins, tpoints, mdamage, multi, divi):
    """
    Compute the Pokemon TCG Battle Points:
      calcfist   = (twins * multi) - tpoints
      calcsecond = ceil(tpoints / divi) - twins
      calcfinal  = calcfist + calcsecond + mdamage
    We avoid floating arithmetic by using integer math for 'ceil'.
    """
    # Equivalent to: calcsecond = ceil(tpoints/divi) - twins
    # For nonnegative tpoints, divi > 0, the "integer ceiling" can be:
    #     (tpoints + divi - 1) // divi
    calcfist   = (twins * multi) - tpoints
    calcsecond = ((tpoints + (divi - 1)) // divi) - twins
    calcfinal  = calcfist + calcsecond + mdamage
    return calcfinal

def entry_point(argv):
    """
    entry_point is the function PyPy looks for when translating to RPython.
    argv is a list of command-line arguments, including the script name at argv[0].
    Return an integer exit code.
    """
    if len(argv) < 4:
        # Minimal usage message
        print("Usage: {} <twins> <tpoints> <mdamage> [--multi X] [--divi Y]".format(argv[0]))
        return 1

    # Parse required arguments
    try:
        twins   = int(argv[1])
        tpoints = int(argv[2])
        mdamage = int(argv[3])
    except:
        print("Invalid integer arguments.")
        return 1

    # Default optional arguments
    multi = 3
    divi  = 3

    # Very simple optional argument handling
    i = 4
    while i < len(argv):
        if argv[i] == "--multi" and (i + 1) < len(argv):
            try:
                multi = int(argv[i + 1])
            except:
                pass
            i += 2
            continue
        elif argv[i] == "--divi" and (i + 1) < len(argv):
            try:
                divi = int(argv[i + 1])
            except:
                pass
            i += 2
            continue
        else:
            i += 1

    result = calc_pokemon_tcg_battle_points(twins, tpoints, mdamage, multi, divi)
    print("Calculated Pokemon TCG Battle Points:", result)
    return 0

def target(*args):
    """
    The target() function is how PyPy's translation toolchain knows
    which 'entry_point' function to use.
    """
    return entry_point

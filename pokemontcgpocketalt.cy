#cython: language_level=3
"""
This program is free software; you can redistribute it and/or modify
it under the terms of the Revised BSD License.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the Revised BSD License for more details.
"""

# In Cython, we can add type annotations to gain speed ups at compile time.
# Here, we define a function that roughly replicates the original Python logic.

from math import ceil

def calc_pokemon_tcg_battle_points(int twins, int tpoints, int mdamage,
                                   int multi=3, int divi=3) -> int:
    """
    Calculate Pokemon TCG Battle Points:
      calcfist   = (twins * multi) - tpoints
      calcsecond = ceil(tpoints / divi) - twins
      calcfinal  = calcfist + calcsecond + mdamage
    """
    cdef int calcfist   = (twins * multi) - tpoints
    cdef int calcsecond = <int>ceil(tpoints / divi) - twins
    cdef int calcfinal  = calcfist + calcsecond + mdamage
    return calcfinal

def main():
    """
    A simple entry point that parses command-line arguments
    and calls calc_pokemon_tcg_battle_points.
    """
    import sys

    args = sys.argv[1:]
    if len(args) < 3:
        sys.stderr.write(f"Usage: {sys.argv[0]} <twins> <tpoints> <mdamage> [--multi X] [--divi Y]\n")
        sys.exit(1)

    twins   = int(args[0])
    tpoints = int(args[1])
    mdamage = int(args[2])

    multi = 3
    divi  = 3

    i = 3
    while i < len(args):
        if args[i] == "--multi" and i + 1 < len(args):
            multi = int(args[i + 1])
            i += 2
        elif args[i] == "--divi" and i + 1 < len(args):
            divi = int(args[i + 1])
            i += 2
        else:
            i += 1

    result = calc_pokemon_tcg_battle_points(twins, tpoints, mdamage, multi, divi)
    print(f"Calculated Pokemon TCG Battle Points: {result}")

# If run as a script, call main().
if __name__ == "__main__":
    main()

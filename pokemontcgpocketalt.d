/*
   This program is free software; you can redistribute it and/or modify
   it under the terms of the Revised BSD License.
   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
   See the Revised BSD License for more details.
*/

import std.stdio;
import std.string;
import std.math;
import std.conv;   // for to!int
import std.array; // for split, etc. if needed

int calcPokemonTCGBattlePotins(int twins, int tpoints, int mdamage, int multi = 3, int divi = 3)
{
    int calcfist = (twins * multi) - tpoints;
    int calcsecond = cast(int)ceil(cast(real)tpoints / cast(real)divi) - twins;
    int calcfinal = calcfist + calcsecond + mdamage;
    return calcfinal;
}

int main(string[] args)
{
    if (args.length < 4) {
        stderr.writefln("Usage: %s <twins> <tpoints> <mdamage> [--multi X] [--divi Y]", args[0]);
        return 1;
    }

    int twins   = to!int(args[1]);
    int tpoints = to!int(args[2]);
    int mdamage = to!int(args[3]);

    int multi = 3;
    int divi  = 3;

    // simple optional argument handling
    for (int i = 4; i < args.length; i++) {
        if (args[i] == "--multi" && i + 1 < args.length) {
            multi = to!int(args[++i]);
        } else if (args[i] == "--divi" && i + 1 < args.length) {
            divi = to!int(args[++i]);
        }
    }

    int result = calcPokemonTCGBattlePotins(twins, tpoints, mdamage, multi, divi);
    writeln("Calculated Pokemon TCG Battle Points: ", result);

    return 0;
}

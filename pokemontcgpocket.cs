/*
   This program is free software; you can redistribute it and/or modify
   it under the terms of the Revised BSD License.
   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  
   See the Revised BSD License for more details.
*/

using System;

class PokemonTCGBattlePoints
{
    static int CalcPokemonTCGBattlePotins(int twins, int tpoints, int mdamage, int multi = 3, int divi = 3)
    {
        int calcfist = (twins * multi) - tpoints;
        double calcSecondD = Math.Ceiling((double)tpoints / divi) - twins;
        int calcsecond = (int)calcSecondD;
        int calcfinal = calcfist + calcsecond + mdamage;
        return calcfinal;
    }

    static void Main(string[] args)
    {
        if (args.Length < 3)
        {
            Console.Error.WriteLine("Usage: PokemonTCGBattlePoints <twins> <tpoints> <mdamage> [--multi X] [--divi Y]");
            return;
        }

        int twins = int.Parse(args[0]);
        int tpoints = int.Parse(args[1]);
        int mdamage = int.Parse(args[2]);

        int multi = 3;
        int divi = 3;

        // Naive argument handling
        for (int i = 3; i < args.Length; i++)
        {
            if (args[i] == "--multi" && i + 1 < args.Length)
            {
                multi = int.Parse(args[++i]);
            }
            else if (args[i] == "--divi" && i + 1 < args.Length)
            {
                divi = int.Parse(args[++i]);
            }
        }

        int result = CalcPokemonTCGBattlePotins(twins, tpoints, mdamage, multi, divi);
        Console.WriteLine("Calculated Pokemon TCG Battle Points: " + result);
    }
}

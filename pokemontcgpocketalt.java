/*
   This program is free software; you can redistribute it and/or modify
   it under the terms of the Revised BSD License.
   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
   See the Revised BSD License for more details.
*/

public class PokemonTCGBattlePoints {
    public static int calcPokemonTCGBattlePotins(int twins, int tpoints, int mdamage, int multi, int divi) {
        int calcfist = (twins * multi) - tpoints;
        int calcsecond = (int)Math.ceil((double)tpoints / (double)divi) - twins;
        int calcfinal = calcfist + calcsecond + mdamage;
        return calcfinal;
    }

    public static void main(String[] args) {
        if (args.length < 3) {
            System.err.println("Usage: java PokemonTCGBattlePoints <twins> <tpoints> <mdamage> [--multi X] [--divi Y]");
            System.exit(1);
        }

        int twins   = Integer.parseInt(args[0]);
        int tpoints = Integer.parseInt(args[1]);
        int mdamage = Integer.parseInt(args[2]);

        int multi = 3;
        int divi  = 3;

        // Simple optional args
        for (int i = 3; i < args.length; i++) {
            if (args[i].equals("--multi") && i + 1 < args.length) {
                multi = Integer.parseInt(args[++i]);
            } else if (args[i].equals("--divi") && i + 1 < args.length) {
                divi = Integer.parseInt(args[++i]);
            }
        }

        int result = calcPokemonTCGBattlePotins(twins, tpoints, mdamage, multi, divi);
        System.out.println("Calculated Pokemon TCG Battle Points: " + result);
    }
}

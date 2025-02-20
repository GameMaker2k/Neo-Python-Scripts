/*
   This program is free software; you can redistribute it and/or modify
   it under the terms of the Revised BSD License.
   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  
   See the Revised BSD License for more details.
*/

#include <stdio.h>
#include <stdlib.h>
#include <math.h>

int CalcPokemonTCGBattlePotins(int twins, int tpoints, int mdamage, int multi, int divi) {
    int calcfist = (twins * multi) - tpoints;
    /* math.ceil(x) in C can be done with ceil((double)x). 
       We need to cast to double, then back to int. */
    int calcsecond = (int)ceil((double)tpoints / (double)divi) - twins;
    int calcfinal = calcfist + calcsecond + mdamage;
    return calcfinal;
}

int main(int argc, char *argv[]) {
    if (argc < 4) {
        fprintf(stderr, "Usage: %s <twins> <tpoints> <mdamage> [--multi X] [--divi Y]\n", argv[0]);
        return 1;
    }

    /* Required arguments */
    int twins = atoi(argv[1]);
    int tpoints = atoi(argv[2]);
    int mdamage = atoi(argv[3]);

    /* Default optional arguments */
    int multi = 3;
    int divi = 3;

    /* Very naive handling of additional args; you might want a real parser. */
    for (int i = 4; i < argc; i++) {
        if (i + 1 < argc && strcmp(argv[i], "--multi") == 0) {
            multi = atoi(argv[++i]);
        } else if (i + 1 < argc && strcmp(argv[i], "--divi") == 0) {
            divi = atoi(argv[++i]);
        }
    }

    int result = CalcPokemonTCGBattlePotins(twins, tpoints, mdamage, multi, divi);
    printf("Calculated Pokemon TCG Battle Points: %d\n", result);

    return 0;
}

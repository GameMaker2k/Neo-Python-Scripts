/*
   This program is free software; you can redistribute it and/or modify
   it under the terms of the Revised BSD License.
   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  
   See the Revised BSD License for more details.
*/

#import <Foundation/Foundation.h>
#import <math.h>

int CalcPokemonTCGBattlePotins(int twins, int tpoints, int mdamage, int multi, int divi) {
    int calcfist = (twins * multi) - tpoints;
    int calcsecond = (int)ceil((double)tpoints / (double)divi) - twins;
    int calcfinal = calcfist + calcsecond + mdamage;
    return calcfinal;
}

int main(int argc, const char * argv[]) {
    @autoreleasepool {
        if (argc < 4) {
            NSLog(@"Usage: %s <twins> <tpoints> <mdamage> [--multi X] [--divi Y]", argv[0]);
            return 1;
        }

        int twins = atoi(argv[1]);
        int tpoints = atoi(argv[2]);
        int mdamage = atoi(argv[3]);

        int multi = 3;
        int divi = 3;

        for (int i = 4; i < argc; i++) {
            if (strcmp(argv[i], "--multi") == 0 && (i + 1) < argc) {
                multi = atoi(argv[++i]);
            } else if (strcmp(argv[i], "--divi") == 0 && (i + 1) < argc) {
                divi = atoi(argv[++i]);
            }
        }

        int result = CalcPokemonTCGBattlePotins(twins, tpoints, mdamage, multi, divi);
        NSLog(@"Calculated Pokemon TCG Battle Points: %d", result);
    }
    return 0;
}

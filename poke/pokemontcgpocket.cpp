/*
   This program is free software; you can redistribute it and/or modify
   it under the terms of the Revised BSD License.
   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  
   See the Revised BSD License for more details.
*/

#include <iostream>
#include <cmath>
#include <string>
#include <vector>

int CalcPokemonTCGBattlePotins(int twins, int tpoints, int mdamage, int multi = 3, int divi = 3) {
    int calcfist = (twins * multi) - tpoints;
    int calcsecond = static_cast<int>(std::ceil(static_cast<double>(tpoints) / static_cast<double>(divi))) - twins;
    int calcfinal = calcfist + calcsecond + mdamage;
    return calcfinal;
}

int main(int argc, char* argv[]) {
    if (argc < 4) {
        std::cerr << "Usage: " << argv[0] 
                  << " <twins> <tpoints> <mdamage> [--multi X] [--divi Y]\n";
        return 1;
    }

    int twins   = std::stoi(argv[1]);
    int tpoints = std::stoi(argv[2]);
    int mdamage = std::stoi(argv[3]);

    int multi = 3;
    int divi  = 3;

    // Simple argument parsing
    for (int i = 4; i < argc; i++) {
        std::string arg = argv[i];
        if (arg == "--multi" && i + 1 < argc) {
            multi = std::stoi(argv[++i]);
        } else if (arg == "--divi" && i + 1 < argc) {
            divi = std::stoi(argv[++i]);
        }
    }

    int result = CalcPokemonTCGBattlePotins(twins, tpoints, mdamage, multi, divi);
    std::cout << "Calculated Pokemon TCG Battle Points: " << result << std::endl;

    return 0;
}

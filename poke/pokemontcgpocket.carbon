// Carbon is still experimental. Example code only.
//
// This program is free software; you can redistribute it and/or modify
// it under the terms of the Revised BSD License.
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
// See the Revised BSD License for more details.

package pokemontcgpocket api;

import math;

fn CalcPokemonTCGBattlePotins(twins: i32, tpoints: i32, mdamage: i32, 
                              multi: i32 = 3, divi: i32 = 3) -> i32 {
  let calcfist: i32 = (twins * multi) - tpoints;
  let calcsecond: i32 = math.ceil(tpoints as f64 / divi as f64) as i32 - twins;
  let calcfinal: i32 = calcfist + calcsecond + mdamage;
  return calcfinal;
}

fn Main() -> i32 {
  // Carbon's argument parsing is not fully specified in the early designs.
  // Pseudocode below:
  var args = Sys.get_arguments();
  if (Size(args) < 4) {
    Print("Usage: {0} <twins> <tpoints> <mdamage> [--multi X] [--divi Y]\n", args[0]);
    return 1;
  }

  var twins = StringToInt(args[1]);
  var tpoints = StringToInt(args[2]);
  var mdamage = StringToInt(args[3]);

  var multi: i32 = 3;
  var divi: i32 = 3;

  // Pseudocode argument handling
  var i: i32 = 4;
  while (i < Size(args)) {
    let arg = args[i];
    if (arg == "--multi" && i + 1 < Size(args)) {
      i = i + 1;
      multi = StringToInt(args[i]);
    } else if (arg == "--divi" && i + 1 < Size(args)) {
      i = i + 1;
      divi = StringToInt(args[i]);
    }
    i = i + 1;
  }

  let result = CalcPokemonTCGBattlePotins(twins, tpoints, mdamage, multi, divi);
  Print("Calculated Pokemon TCG Battle Points: {0}\n", result);
  return 0;
}

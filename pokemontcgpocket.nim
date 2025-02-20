# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the Revised BSD License for more details.
#

import math, strutils

proc CalcPokemonTCGBattlePotins(twins, tpoints, mdamage: int; multi = 3, divi = 3): int =
  let calcfist = (twins * multi) - tpoints
  # We need a floating calculation for ceil:
  let calcsecond = ceil(float(tpoints) / float(divi)) - float(twins)
  return calcfist + int(calcsecond) + mdamage

when isMainModule:
  if paramCount() < 3:
    echo "Usage: ", paramStr(0), " <twins> <tpoints> <mdamage> [--multi X] [--divi Y]"
    quit(1)

  let twins = parseInt(paramStr(1))
  let tpoints = parseInt(paramStr(2))
  let mdamage = parseInt(paramStr(3))

  var multi = 3
  var divi = 3

  # Naive optional argument handling
  var i = 4
  while i <= paramCount():
    let arg = paramStr(i)
    if arg == "--multi" and i+1 <= paramCount():
      multi = parseInt(paramStr(i+1))
      i += 1
    elif arg == "--divi" and i+1 <= paramCount():
      divi = parseInt(paramStr(i+1))
      i += 1
    i += 1

  let result = CalcPokemonTCGBattlePotins(twins, tpoints, mdamage, multi, divi)
  echo "Calculated Pokemon TCG Battle Points: ", result

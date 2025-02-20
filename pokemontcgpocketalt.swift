/*
   This program is free software; you can redistribute it and/or modify
   it under the terms of the Revised BSD License.
   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
   See the Revised BSD License for more details.
*/

import Foundation

func calcPokemonTCGBattlePotins(_ twins: Int, _ tpoints: Int, _ mdamage: Int, multi: Int = 3, divi: Int = 3) -> Int {
    let calcfist = (twins * multi) - tpoints
    // Foundation's ceil works on Double
    let calcsecond = Int(ceil(Double(tpoints) / Double(divi))) - twins
    let calcfinal = calcfist + calcsecond + mdamage
    return calcfinal
}

// Get Command-line arguments (excluding the executable name)
let args = CommandLine.arguments.dropFirst() // ArraySlice<String>

if args.count < 3 {
    fputs("Usage: \(CommandLine.arguments[0]) <twins> <tpoints> <mdamage> [--multi X] [--divi Y]\n", stderr)
    exit(1)
}

guard let twins   = Int(args[0]),
      let tpoints = Int(args[1]),
      let mdamage = Int(args[2]) else {
    fputs("Invalid integer arguments.\n", stderr)
    exit(1)
}

var multi = 3
var divi = 3

var i = 3
while i < args.count {
    switch args[i] {
    case "--multi":
        i += 1
        if i < args.count, let m = Int(args[i]) {
            multi = m
        }
    case "--divi":
        i += 1
        if i < args.count, let d = Int(args[i]) {
            divi = d
        }
    default:
        break
    }
    i += 1
}

let result = calcPokemonTCGBattlePotins(twins, tpoints, mdamage, multi: multi, divi: divi)
print("Calculated Pokemon TCG Battle Points: \(result)")

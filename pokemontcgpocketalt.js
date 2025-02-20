#!/usr/bin/env node
/*
   This program is free software; you can redistribute it and/or modify
   it under the terms of the Revised BSD License.
   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
   See the Revised BSD License for more details.
*/

function calcPokemonTCGBattlePotins(twins, tpoints, mdamage, multi = 3, divi = 3) {
  const calcfist = (twins * multi) - tpoints;
  const calcsecond = Math.ceil(tpoints / divi) - twins;
  const calcfinal = calcfist + calcsecond + mdamage;
  return calcfinal;
}

// Naive CLI argument handling
const args = process.argv.slice(2); 
// Example: node pokemontcgpocket.js 10 20 30 --multi 3 --divi 3

if (args.length < 3) {
  console.error(`Usage: ${process.argv[1]} <twins> <tpoints> <mdamage> [--multi X] [--divi Y]`);
  process.exit(1);
}

let twins   = parseInt(args[0], 10);
let tpoints = parseInt(args[1], 10);
let mdamage = parseInt(args[2], 10);

let multi = 3;
let divi  = 3;

// Very naive handling of optional args
for (let i = 3; i < args.length; i++) {
  if (args[i] === '--multi' && i + 1 < args.length) {
    multi = parseInt(args[++i], 10);
  } else if (args[i] === '--divi' && i + 1 < args.length) {
    divi = parseInt(args[++i], 10);
  }
}

const result = cal

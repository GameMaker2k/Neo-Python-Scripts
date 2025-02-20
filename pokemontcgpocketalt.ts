/*
   This program is free software; you can redistribute it and/or modify
   it under the terms of the Revised BSD License.
   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
   See the Revised BSD License for more details.
*/

function calcPokemonTCGBattlePotins(
  twins: number,
  tpoints: number,
  mdamage: number,
  multi: number = 3,
  divi: number = 3
): number {
  const calcfist = (twins * multi) - tpoints;
  const calcsecond = Math.ceil(tpoints / divi) - twins;
  const calcfinal = calcfist + calcsecond + mdamage;
  return calcfinal;
}

// Naive CLI argument handling with Node
const args = process.argv.slice(2); 
// Example: npx ts-node pokemontcgpocket.ts 10 20 30 --multi 3 --divi 3

if (args.length < 3) {
  console.error(`Usage: ts-node pokemontcgpocket.ts <twins> <tpoints> <mdamage> [--multi X] [--divi Y]`);
  process.exit(1);
}

let twins   = parseInt(args[0], 10);
let tpoints = parseInt(args[1], 10);
let mdamage = parseInt(args[2], 10);

let multi = 3;
let divi  = 3;

for (let i = 3; i < args.length; i++) {
  if (args[i] === '--multi' && i + 1 < args.length) {
    multi = parseInt(args[++i], 10);
  } else if (args[i] === '--divi' && i + 1 < args.length) {
    divi = parseInt(args[++i], 10);
  }
}

const result = calcPokemonTCGBattlePotins(twins, tpoints, mdamage, multi, divi);
console.log(`Calculated Pokemon TCG Battle Points: ${result}`);

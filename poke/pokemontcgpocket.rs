/*
   This program is free software; you can redistribute it and/or modify
   it under the terms of the Revised BSD License.
   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  
   See the Revised BSD License for more details.
*/

use std::env;
use std::f64;

fn calc_pokemon_tcg_battle_points(twins: i32, tpoints: i32, mdamage: i32, multi: i32, divi: i32) -> i32 {
    let calcfist = (twins * multi) - tpoints;
    let calcsecond = (tpoints as f64 / divi as f64).ceil() as i32 - twins;
    let calcfinal = calcfist + calcsecond + mdamage;
    calcfinal
}

fn main() {
    let args: Vec<String> = env::args().collect();

    if args.len() < 4 {
        eprintln!("Usage: {} <twins> <tpoints> <mdamage> [--multi X] [--divi Y]", args[0]);
        std::process::exit(1);
    }

    let twins   = args[1].parse::<i32>().expect("Invalid twins");
    let tpoints = args[2].parse::<i32>().expect("Invalid tpoints");
    let mdamage = args[3].parse::<i32>().expect("Invalid mdamage");

    let mut multi = 3;
    let mut divi = 3;

    let mut i = 4;
    while i < args.len() {
        match args[i].as_str() {
            "--multi" => {
                i += 1;
                if i < args.len() {
                    multi = args[i].parse().unwrap_or(3);
                }
            },
            "--divi" => {
                i += 1;
                if i < args.len() {
                    divi = args[i].parse().unwrap_or(3);
                }
            },
            _ => {}
        }
        i += 1;
    }

    let result = calc_pokemon_tcg_battle_points(twins, tpoints, mdamage, multi, divi);
    println!("Calculated Pokemon TCG Battle Points: {}", result);
}

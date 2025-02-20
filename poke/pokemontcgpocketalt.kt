/*
   This program is free software; you can redistribute it and/or modify
   it under the terms of the Revised BSD License.
   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
   See the Revised BSD License for more details.
*/

import kotlin.math.ceil

fun calcPokemonTCGBattlePotins(twins: Int, tpoints: Int, mdamage: Int, multi: Int = 3, divi: Int = 3): Int {
    val calcfist   = (twins * multi) - tpoints
    val calcsecond = ceil(tpoints.toDouble() / divi.toDouble()).toInt() - twins
    val calcfinal  = calcfist + calcsecond + mdamage
    return calcfinal
}

fun main(args: Array<String>) {
    if (args.size < 3) {
        System.err.println("Usage: <program> <twins> <tpoints> <mdamage> [--multi X] [--divi Y]")
        return
    }

    val twins   = args[0].toIntOrNull() ?: error("Invalid twins")
    val tpoints = args[1].toIntOrNull() ?: error("Invalid tpoints")
    val mdamage = args[2].toIntOrNull() ?: error("Invalid mdamage")

    var multi = 3
    var divi  = 3

    var i = 3
    while (i < args.size) {
        when (args[i]) {
            "--multi" -> {
                i++
                if (i < args.size) {
                    multi = args[i].toIntOrNull() ?: multi
                }
            }
            "--divi" -> {
                i++
                if (i < args.size) {
                    divi = args[i].toIntOrNull() ?: divi
                }
            }
        }
        i++
    }

    val result = calcPokemonTCGBattlePotins(twins, tpoints, mdamage, multi, divi)
    println("Calculated Pokemon TCG Battle Points: $result")
}

/*
   This program is free software; you can redistribute it and/or modify
   it under the terms of the Revised BSD License.
   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
   See the Revised BSD License for more details.
*/

package main

import (
    "fmt"
    "math"
    "os"
    "strconv"
)

func calcPokemonTCGBattlePotins(twins, tpoints, mdamage, multi, divi int) int {
    calcfist := (twins * multi) - tpoints
    calcsecond := int(math.Ceil(float64(tpoints)/float64(divi))) - twins
    calcfinal := calcfist + calcsecond + mdamage
    return calcfinal
}

func main() {
    args := os.Args[1:] // skip program name

    if len(args) < 3 {
        fmt.Fprintf(os.Stderr, "Usage: %s <twins> <tpoints> <mdamage> [--multi X] [--divi Y]\n", os.Args[0])
        os.Exit(1)
    }

    twins, err1 := strconv.Atoi(args[0])
    tpoints, err2 := strconv.Atoi(args[1])
    mdamage, err3 := strconv.Atoi(args[2])
    if err1 != nil || err2 != nil || err3 != nil {
        fmt.Fprintln(os.Stderr, "Invalid integer arguments.")
        os.Exit(1)
    }

    multi := 3
    divi := 3

    i := 3
    for i < len(args) {
        switch args[i] {
        case "--multi":
            if i+1 < len(args) {
                m, err := strconv.Atoi(args[i+1])
                if err == nil {
                    multi = m
                }
                i++
            }
        case "--divi":
            if i+1 < len(args) {
                d, err := strconv.Atoi(args[i+1])
                if err == nil {
                    divi = d
                }
                i++
            }
        }
        i++
    }

    result := calcPokemonTCGBattlePotins(twins, tpoints, mdamage, multi, divi)
    fmt.Printf("Calculated Pokemon TCG Battle Points: %d\n", result)
}

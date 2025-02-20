#!/usr/bin/env Rscript
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the Revised BSD License for more details.
#

calcPokemonTCGBattlePotins <- function(twins, tpoints, mdamage, multi=3, divi=3) {
  calcfist   <- (twins * multi) - tpoints
  calcsecond <- ceiling(tpoints / divi) - twins
  calcfinal  <- calcfist + calcsecond + mdamage
  return(calcfinal)
}

args <- commandArgs(trailingOnly = TRUE)
# e.g. Rscript pokemontcgpocket.R 10 20 30 --multi 3 --divi 3

if (length(args) < 3) {
  cat(sprintf("Usage: %s <twins> <tpoints> <mdamage> [--multi X] [--divi Y]\n", 
              sys.argv()[1]))
  quit(status=1)
}

twins   <- as.integer(args[1])
tpoints <- as.integer(args[2])
mdamage <- as.integer(args[3])

multi <- 3
divi  <- 3

i <- 4
while (i <= length(args)) {
  if (args[i] == "--multi" && i+1 <= length(args)) {
    i <- i + 1
    multi <- as.integer(args[i])
  } else if (args[i] == "--divi" && i+1 <= length(args)) {
    i <- i + 1
    divi <- as.integer(args[i])
  }
  i <- i + 1
}

result <- calcPokemonTCGBattlePotins(twins, tpoints, mdamage, multi, divi)
cat(sprintf("Calculated Pokemon TCG Battle Points: %d\n", result))

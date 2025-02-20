#!/usr/bin/env php
<?php
/*
   This program is free software; you can redistribute it and/or modify
   it under the terms of the Revised BSD License.
   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
   See the Revised BSD License for more details.
*/

function CalcPokemonTCGBattlePotins($twins, $tpoints, $mdamage, $multi = 3, $divi = 3) {
    $calcfist = ($twins * $multi) - $tpoints;
    $calcsecond = ceil($tpoints / $divi) - $twins;
    $calcfinal = $calcfist + $calcsecond + $mdamage;
    return $calcfinal;
}

// Simple CLI argument handling
$args = $argv;
array_shift($args); // remove script name

if (count($args) < 3) {
    fwrite(STDERR, "Usage: php pokemontcgpocket.php <twins> <tpoints> <mdamage> [--multi X] [--divi Y]\n");
    exit(1);
}

// Required arguments
$twins   = (int)$args[0];
$tpoints = (int)$args[1];
$mdamage = (int)$args[2];

// Default optional arguments
$multi = 3;
$divi  = 3;

// Naive handling of additional arguments
for ($i = 3; $i < count($args); $i++) {
    if ($args[$i] === '--multi' && isset($args[$i+1])) {
        $multi = (int)$args[++$i];
    } else if ($args[$i] === '--divi' && isset($args[$i+1])) {
        $divi = (int)$args[++$i];
    }
}

$result = CalcPokemonTCGBattlePotins($twins, $tpoints, $mdamage, $multi, $divi);
echo "Calculated Pokemon TCG Battle Points: $result\n";

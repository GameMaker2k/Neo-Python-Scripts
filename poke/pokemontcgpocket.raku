#!/usr/bin/env raku
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the Revised BSD License for more details.
#

sub CalcPokemonTCGBattlePotins(Int $twins, Int $tpoints, Int $mdamage, Int $multi = 3, Int $divi = 3) {
    my $calcfist   = ($twins * $multi) - $tpoints;
    my $calcsecond = ($tpoints / $divi).ceiling - $twins;
    my $calcfinal  = $calcfist + $calcsecond + $mdamage;
    return $calcfinal;
}

my @args = @*ARGS;

if @args < 3 {
    say "Usage: $*PROGRAM-NAME <twins> <tpoints> <mdamage> [--multi X] [--divi Y]";
    exit 1;
}

my Int $twins   = @args[0].Int;
my Int $tpoints = @args[1].Int;
my Int $mdamage = @args[2].Int;

my Int $multi = 3;
my Int $divi  = 3;

my $i = 3;
while $i < @args.elems {
    given @args[$i] {
        when '--multi' {
            $i++;
            if $i < @args.elems { $multi = @args[$i].Int }
        }
        when '--divi' {
            $i++;
            if $i < @args.elems { $divi = @args[$i].Int }
        }
        default { }
    }
    $i++;
}

my $result = CalcPokemonTCGBattlePotins($twins, $tpoints, $mdamage, $multi, $divi);
say "Calculated Pokemon TCG Battle Points: $result";

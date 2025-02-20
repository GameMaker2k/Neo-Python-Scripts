#!/usr/bin/env perl
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the Revised BSD License for more details.
#

use strict;
use warnings;
use POSIX 'ceil';

sub CalcPokemonTCGBattlePotins {
    my ($twins, $tpoints, $mdamage, $multi, $divi) = @_;
    $multi //= 3;
    $divi  //= 3;

    my $calcfist   = ($twins * $multi) - $tpoints;
    my $calcsecond = ceil($tpoints / $divi) - $twins;
    # or more simply: my $calcsecond = POSIX::ceil($tpoints/$divi) - $twins; if you "use POSIX 'ceil';"

    my $calcfinal  = $calcfist + $calcsecond + $mdamage;
    return $calcfinal;
}

my @args = @ARGV;
if (@args < 3) {
    die "Usage: $0 <twins> <tpoints> <mdamage> [--multi X] [--divi Y]\n";
}

my $twins   = shift @args;
my $tpoints = shift @args;
my $mdamage = shift @args;

my $multi = 3;
my $divi  = 3;

while (@args) {
    my $arg = shift @args;
    if ($arg eq '--multi' && @args) {
        $multi = shift @args;
    } elsif ($arg eq '--divi' && @args) {
        $divi = shift @args;
    }
}

my $result = CalcPokemonTCGBattlePotins($twins, $tpoints, $mdamage, $multi, $divi);
print "Calculated Pokemon TCG Battle Points: $result\n";

#!/usr/bin/env raku

sub MAIN(
    Int :$twins,
    Int :$tpoints,
    Int :$mdamage,
    Int :$multi = 3,
    Int :$divi = 3
) {
    sub CalcPokemonTCGBattlePotins($twins, $tpoints, $mdamage, $multi, $divi) {
        my $calcfist   = ($twins * $multi) - $tpoints;
        my $calcsecond = ($tpoints / $divi).ceiling - $twins;
        my $calcfinal  = $calcfist + $calcsecond + $mdamage;
        return $calcfinal;
    }
    my $result = CalcPokemonTCGBattlePotins($twins, $tpoints, $mdamage, $multi, $divi);
    say "Calculated Pokemon TCG Battle Points: $result";
}

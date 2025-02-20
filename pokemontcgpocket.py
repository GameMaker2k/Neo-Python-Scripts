# Random Pokemon TCG Pocket Calc App

def CalcPokemonTCGBattlePotins(twins, tpoints, mdamage, multi=3, divi=3):
    calcfist = (twins * multi) -  tpoints
    calcsecond = (tpoints / divi) - twins
    calcfinal = (calcfist + calcsecond) + mdamage

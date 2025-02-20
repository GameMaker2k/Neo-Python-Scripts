-- 
-- This program is free software; you can redistribute it and/or modify
-- it under the terms of the Revised BSD License.
-- This program is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
-- See the Revised BSD License for more details.
--

CREATE OR REPLACE FUNCTION calc_pokemon_tcg_battle_potins(
    p_twins   int,
    p_tpoints int,
    p_mdamage int,
    p_multi   int default 3,
    p_divi    int default 3
)
RETURNS int
LANGUAGE plpgsql
AS $$
DECLARE
    calcfist   int;
    calcsecond int;
    calcfinal  int;
BEGIN
    calcfist   = (p_twins * p_multi) - p_tpoints;
    calcsecond = ceil(p_tpoints::numeric / p_divi::numeric)::int - p_twins;
    calcfinal  = calcfist + calcsecond + p_mdamage;

    RETURN calcfinal;
END;
$$;

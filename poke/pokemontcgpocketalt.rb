#!/usr/bin/env ruby
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the Revised BSD License for more details.
#

def calc_pokemon_tcg_battle_potins(twins, tpoints, mdamage, multi=3, divi=3)
  calcfist = (twins * multi) - tpoints
  calcsecond = (tpoints.to_f / divi.to_f).ceil - twins
  calcfinal = calcfist + calcsecond + mdamage
  return calcfinal
end

args = ARGV

if args.size < 3
  $stderr.puts "Usage: #{$0} <twins> <tpoints> <mdamage> [--multi X] [--divi Y]"
  exit 1
end

twins   = args[0].to_i
tpoints = args[1].to_i
mdamage = args[2].to_i

multi = 3
divi = 3

i = 3
while i < args.size
  case args[i]
  when '--multi'
    i += 1
    multi = args[i].to_i if i < args.size
  when '--divi'
    i += 1
    divi = args[i].to_i if i < args.size
  end
  i += 1
end

result = calc_pokemon_tcg_battle_potins(twins, tpoints, mdamage, multi, divi)
puts "Calculated Pokemon TCG Battle Points: #{result}"

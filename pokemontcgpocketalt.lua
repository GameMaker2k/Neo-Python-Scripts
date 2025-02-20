#!/usr/bin/env lua
--[[
   This program is free software; you can redistribute it and/or modify
   it under the terms of the Revised BSD License.
   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
   See the Revised BSD License for more details.
]]

local function calcPokemonTCGBattlePotins(twins, tpoints, mdamage, multi, divi)
  local calcfist   = (twins * multi) - tpoints
  local calcsecond = math.ceil(tpoints / divi) - twins
  local calcfinal  = calcfist + calcsecond + mdamage
  return calcfinal
end

-- CLI argument handling
local args = { ... } -- or use arg, which is a table for command-line arguments
if #args < 3 then
  io.stderr:write(string.format("Usage: %s <twins> <tpoints> <mdamage> [--multi X] [--divi Y]\n", arg[0]))
  os.exit(1)
end

local twins   = tonumber(args[1])
local tpoints = tonumber(args[2])
local mdamage = tonumber(args[3])

local multi = 3
local divi  = 3

-- Simple optional-argument parsing
local i = 4
while i <= #args do
  if args[i] == "--multi" and (i+1) <= #args then
    multi = tonumber(args[i+1]) or 3
    i = i + 1
  elseif args[i] == "--divi" and (i+1) <= #args then
    divi = tonumber(args[i+1]) or 3
    i = i + 1
  end
  i = i + 1
end

local result = calcPokemonTCGBattlePotins(twins, tpoints, mdamage, multi, divi)
print(string.format("Calculated Pokemon TCG Battle Points: %d", result))

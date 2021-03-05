#!/bin/env python

# 12 volts multiplied 5 amps equals 60 watts
def get_watts_from_volts_and_amps(volts, amps):
 return int(volts * amps);

print(str(get_watts_from_volts_and_amps(12, 5))+" watts");

# 60 watts divided 5 amps equals 12 volts
def get_volts_from_watts_and_amps(watts, amps):
 return int(watts / amps);

print(str(get_volts_from_watts_and_amps(60, 5))+" volts");

# 60 watts divided by 12 volts equals 5 amps
def get_amps_from_watts_and_volts(watts, volts):
 return int(watts / volts);

print(str(get_amps_from_watts_and_volts(60, 12))+" amps");

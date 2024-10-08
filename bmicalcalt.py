#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

'''
    This program is free software; you can redistribute it and/or modify
    it under the terms of the Revised BSD License.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    Revised BSD License for more details.

    Copyright 2016 Game Maker 2k - https://github.com/GameMaker2k
    Copyright 2016 Joshua Przyborowski - https://github.com/JoshuaPrzyborowski

    $FileInfo: bmicalc.py - Last Update: 08/15/2017 Ver. 0.0.1 RC 2 - Author: joshuatp $
'''

import argparse
import math


def cal_lbs_to_kg(lbs):
    """Convert pounds to kilograms."""
    return lbs * 0.45359237


def cal_kg_to_lbs(kg):
    """Convert kilograms to pounds."""
    return kg / 0.45359237


def cal_fet_ins_to_cm(fet, ins):
    """Convert feet and inches to centimeters."""
    allins = (fet * 12) + ins
    return allins * 2.54


def cal_cm_to_fet_ins(cm):
    """Convert centimeters to feet and inches."""
    ins = int(cm * 0.3937008)
    retfet = int(ins / 12)
    retins = int(ins % 12)
    return retfet, retins


def cal_bmi_imperial(lbs, fet, ins):
    """Calculate BMI using Imperial units."""
    allins = (fet * 12) + ins
    inscalc = allins * allins
    return lbs / inscalc * 703


def cal_bmi_metric(kg, cm):
    """Calculate BMI using Metric units."""
    allmet = cm / 100
    metcalc = allmet * allmet
    return kg / metcalc


def cal_bmi_imperial_alt(lbs, fet, ins):
    """Calculate BMI using Imperial units, but convert to Metric for calculation."""
    kg = cal_lbs_to_kg(lbs)
    cm = cal_fet_ins_to_cm(fet, ins)
    return cal_bmi_metric(kg, cm)


def cal_bmi_metric_alt(kg, cm):
    """Calculate BMI using Metric units, but convert to Imperial for calculation."""
    lbs = cal_kg_to_lbs(kg)
    fet, ins = cal_cm_to_fet_ins(cm)
    return cal_bmi_imperial(lbs, fet, ins)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--weight", type=float,
                        required=True, help="Weight in kilograms or pounds")
    parser.add_argument("-hi", "--height_inches",
                        type=float, help="Height in inches")
    parser.add_argument("-hf", "--height_feet",
                        type=float, help="Height in feet")
    parser.add_argument("-hc", "--height_cm", type=float,
                        help="Height in centimeters")
    parser.add_argument(
        "-s",
        "--system",
        choices=[
            "imperial",
            "metric"],
        required=True,
        help="Measurement system to use")
    args = parser.parse_args()

    if args.system == "imperial":
        print(
            cal_bmi_imperial(
                args.weight,
                args.height_feet,
                args.height_inches))
    elif args.system == "metric":
        print(cal_bmi_metric(args.weight, args.height_cm))

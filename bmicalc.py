#!/usr/bin/python

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

import math


def cal_lbs_to_kg(lbs):
    kg = lbs * 0.45359237
    return kg


def cal_kg_to_lbs(kg):
    lbs = kg / 0.45359237
    return lbs


def cal_ins_to_fet_ins(ins):
    retfet = int(ins / 12)
    retins = int(ins % 12)
    return float(str(int(retfet))+"."+str(int(retins)))


def cal_fet_ins_to_cm(fet, ins):
    allins = (fet * 12) + ins
    cm = allins * 2.54
    return cm


def cal_ins_to_cm(ins):
    cm = ins * 2.54
    return cm


def cal_cm_to_fet_ins(cm):
    ins = int(cm * 0.3937008)
    retfet = int(ins / 12)
    retins = int(ins % 12)
    return float(str(int(retfet))+"."+str(int(retins)))


def cal_cm_to_ins(cm):
    ins = int(cm * 0.3937008)
    return ins


def cal_bmi_imperial(lbs, fet, ins):
    allins = (fet * 12) + ins
    inscalc = allins * allins
    bmi = lbs / inscalc * 703
    f_bmi = math.floor(bmi)
    diff = bmi - f_bmi
    diff = diff * 10
    diff = round(diff)
    if(diff == 10):
        f_bmi = f_bmi + 1
        diff = 0
    bmi = float(str(int(f_bmi))+"."+str(int(diff)))
    return bmi


def cal_bmi_metric(kg, cm):
    allmet = cm / 100
    metcalc = allmet * allmet
    bmi = kg / metcalc
    f_bmi = math.floor(bmi)
    diff = bmi - f_bmi
    diff = diff * 10
    diff = round(diff)
    if(diff == 10):
        f_bmi = f_bmi + 1
        diff = 0
    bmi = float(str(int(f_bmi))+"."+str(int(diff)))
    return bmi


def cal_bmi_imperial_alt(lbs, fet, ins):
    kg = cal_lbs_to_kg(lbs)
    cm = cal_fet_ins_to_cm(fet, ins)
    bmi = cal_bmi_metric(kg, cm)
    return bmi


def cal_bmi_metric_alt(kg, cm):
    lbs = cal_kg_to_lbs(kg)
    predec = str(cal_cm_to_fet_ins(cm)).split('.')
    fet = int(predec[0])
    ins = int(predec[1])
    bmi = cal_bmi_imperial(lbs, fet, ins)
    return bmi


print(str(cal_bmi_imperial(150, 5, 11)))
print(str(cal_bmi_metric(68, 180.34)))
print(str(cal_bmi_imperial_alt(150, 5, 11)))
print(str(cal_bmi_metric_alt(68, 180.34)))

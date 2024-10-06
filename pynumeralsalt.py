#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    This program is free software; you can redistribute it and/or modify
    it under the terms of the Revised BSD License.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    Revised BSD License for more details.

    Copyright 2019 Game Maker 2k - https://github.com/GameMaker2k
    Copyright 2019 Kazuki Przyborowski - https://github.com/KazukiPrzyborowski

    $FileInfo: pynumerals.py - Last Update: 12/22/2021 Ver. 0.0.1 RC 1 - Author: kazukisp $
'''

western_arabic = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
eastern_arabic = ['٠', '١', '٢', '٣', '٤', '٥', '٦', '٧', '٨', '٩']
persian = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹']
urdu = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹']

# Dictionaries for converting between different numeral systems
western_to_eastern = {western_arabic[i]: eastern_arabic[i] for i in range(10)}
western_to_persian = {western_arabic[i]: persian[i] for i in range(10)}
western_to_urdu = {western_arabic[i]: urdu[i] for i in range(10)}

eastern_to_western = {eastern_arabic[i]: western_arabic[i] for i in range(10)}
eastern_to_persian = {eastern_arabic[i]: persian[i] for i in range(10)}
eastern_to_urdu = {eastern_arabic[i]: urdu[i] for i in range(10)}

persian_to_western = {persian[i]: western_arabic[i] for i in range(10)}
persian_to_eastern = {persian[i]: eastern_arabic[i] for i in range(10)}
persian_to_urdu = {persian[i]: urdu[i] for i in range(10)}

urdu_to_western = {urdu[i]: western_arabic[i] for i in range(10)}
urdu_to_eastern = {urdu[i]: eastern_arabic[i] for i in range(10)}
urdu_to_persian = {urdu[i]: persian[i] for i in range(10)}

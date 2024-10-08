#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    This program is free software; you can redistribute it and/or modify
    it under the terms of the Revised BSD License.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    Revised BSD License for more details.

    Copyright 2024 Game Maker 2k - https://github.com/GameMaker2k
    Copyright 2024 Kazuki Przyborowski - https://github.com/KazukiPrzyborowski

    $FileInfo: farsi_to_latin.py - Last Update: 5/31/2024 Ver. 1.0.0 RC 1 - Author: joshuatp $
'''

import os

# Comprehensive conversion dictionaries for Persian script
arabic_to_latin_farsi = {
    'ا': 'A', 'ب': 'B', 'پ': 'P', 'ت': 'T', 'ث': 'S', 'ج': 'J', 'چ': 'Č', 'ح': 'H', 'خ': 'Kh', 'د': 'D',
    'ذ': 'Z', 'ر': 'R', 'ز': 'Z', 'ژ': 'Ž', 'س': 'S', 'ش': 'Sh', 'ص': 'Ṣ', 'ض': 'Ẓ', 'ط': 'Ṭ', 'ظ': 'Ẓ',
    'ع': 'ʿ', 'غ': 'Gh', 'ف': 'F', 'ق': 'Q', 'ک': 'K', 'گ': 'G', 'ل': 'L', 'م': 'M', 'ن': 'N', 'و': 'V',
    # ZWNJ replaced with space
    'ه': 'H', 'ی': 'Y', 'آ': 'Ā', ' ': ' ', '،': ',', '؟': '?', '؛': ';', '!': '!', '‌': ' ',
    'ء': "'", 'ً': 'an', 'َ': 'a', 'ُ': 'u', 'ِ': 'i', 'ّ': '', 'ْ': '', 'ٔ': '', 'ٓ': '',
    'ئ': 'Y', 'ي': 'i', 'ك': 'K', 'ى': 'A', '«': '"', '»': '"', '(': '(', ')': ')',
    '۱': '1', '۲': '2', '۳': '3', '۴': '4', '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9', '۰': '0',
    '.': '.', ':': ':', '—': '-', '\n': '\n', '\r': '\r', '[': '[', ']': ']'
}

# Ensuring correct round-trip conversion
latin_to_arabic_farsi = {
    'A': 'ا',
    'B': 'ب',
    'P': 'پ',
    'T': 'ت',
    'S': 'ث',
    'J': 'ج',
    'Č': 'چ',
    'H': 'ح',
    'Kh': 'خ',
    'D': 'د',
    'Z': 'ز',
    'R': 'ر',
    'Ž': 'ژ',
    'Sh': 'ش',
    'Ṣ': 'ص',
    'Ẓ': 'ض',
    'Ṭ': 'ط',
    'Ẓ': 'ظ',
    'ʿ': 'ع',
    'Gh': 'غ',
    'F': 'ف',
    'Q': 'ق',
    'K': 'ک',
    'G': 'گ',
    'L': 'ل',
    'M': 'م',
    'N': 'ن',
    'V': 'و',
    'Y': 'ی',
    'Ā': 'آ',
    'i': 'ي',
    ' ': ' ',
    ',': '،',
    '?': '؟',
    ';': '؛',
    '!': '!',
    ' ': '‌',
    "'": 'ء',
    'an': 'ً',
    'a': 'َ',
    'u': 'ُ',
    'i': 'ِ',
    '': 'ّ',
    '': 'ْ',
    '': 'ٔ',
    '': 'ٓ',
    '"': '«',
    '(': '(',
    ')': ')',
    '1': '۱',
    '2': '۲',
    '3': '۳',
    '4': '۴',
    '5': '۵',
    '6': '۶',
    '7': '۷',
    '8': '۸',
    '9': '۹',
    '0': '۰',
    '.': '.',
    ':': ':',
    '-': '—',
    '\n': '\n',
    '\r': '\r',
    '[': '[',
    ']': ']'}

# Function to convert Farsi script to Latin-based script


def farsi_to_latin_script(text):
    result = ''
    for char in text:
        result += arabic_to_latin_farsi.get(char, char)
    return result

# Function to convert Latin-based script to Farsi script


def latin_to_farsi_script(text):
    result = ''
    for char in text:
        result += latin_to_arabic_farsi.get(char, char)
    return result

# Function to read text from a file


def read_text_file(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# Function to write text to a file


def write_text_file(file_path, text):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(text)

# Function to convert a file from Farsi script to Latin-based script and
# save it to another file


def convert_farsi_file_to_latin(input_file_path, output_file_path):
    farsi_text = read_text_file(input_file_path)
    latin_text = farsi_to_latin_script(farsi_text)
    write_text_file(output_file_path, latin_text)

# Function to convert a file from Latin-based script to Farsi script and
# save it to another file


def convert_latin_file_to_farsi(input_file_path, output_file_path):
    latin_text = read_text_file(input_file_path)
    farsi_text = latin_to_farsi_script(latin_text)
    write_text_file(output_file_path, farsi_text)

# Function to convert a file from Farsi script to Latin-based script and
# return the result as a variable


def convert_farsi_file_to_latin_variable(input_file_path):
    farsi_text = read_text_file(input_file_path)
    return farsi_to_latin_script(farsi_text)

# Function to convert a file from Latin-based script to Farsi script and
# return the result as a variable


def convert_latin_file_to_farsi_variable(input_file_path):
    latin_text = read_text_file(input_file_path)
    return latin_to_farsi_script(latin_text)

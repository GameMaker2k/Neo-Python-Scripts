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

    $FileInfo: pashto_to_latin.py - Last Update: 5/31/2024 Ver. 1.0.0 RC 1 - Author: joshuatp $
'''

# Comprehensive conversion dictionaries for Pashto script
arabic_to_latin_pashto = {
    'ا': 'A', 'ب': 'B', 'پ': 'P', 'ت': 'T', 'ټ': 'Ṭ', 'ث': 'S', 'ج': 'J', 'ځ': 'Dz', 'چ': 'Č', 'څ': 'Ts',
    'ح': 'H', 'خ': 'Kh', 'د': 'D', 'ډ': 'Ḍ', 'ذ': 'Z', 'ر': 'R', 'ړ': 'Ṙ', 'ز': 'Z', 'ژ': 'Zh', 'س': 'S',
    'ش': 'Sh', 'ص': 'Ṣ', 'ض': 'Ẓ', 'ط': 'Ṭ', 'ظ': 'Ẓ', 'ع': 'ʿ', 'غ': 'Gh', 'ف': 'F', 'ق': 'Q', 'ک': 'K',
    'ګ': 'G', 'گ': 'G', 'ل': 'L', 'م': 'M', 'ن': 'N', 'ڼ': 'Ṉ', 'و': 'W', 'ه': 'H', 'ۀ': 'H', 'ی': 'Y',
    'ې': 'Ē', 'ئ': 'Y', 'ۍ': 'Yi', 'ې': 'Yē', 'ى': 'A', 'آ': 'Ā', ' ': ' ', '،': ',', '؟': '?', '؛': ';',
    '!': '!', '‌': ' ',  # ZWNJ replaced with space
    'ء': "'", 'ً': 'an', 'َ': 'a', 'ُ': 'u', 'ِ': 'i', 'ّ': '', 'ْ': '', 'ٔ': '', 'ٓ': '',
    'ي': 'i', 'ك': 'K', '«': '"', '»': '"', '(': '(', ')': ')', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
    '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9', '۰': '0', '.': '.', ':': ':', '—': '-',
    '\n': '\n', '\r': '\r', '[': '[', ']': ']', 'پ': 'P', 'ښ': 'x', 'ش': 'Sh', 'ټ': 'Ṭ', 'څ': 'Ts'
}

latin_to_arabic_pashto = {v: k for k, v in arabic_to_latin_pashto.items()}

# Function to convert Pashto script to Latin-based script
def pashto_to_latin_script(text):
    result = ''
    i = 0
    while i < len(text):
        if i + 1 < len(text) and text[i:i+2] in arabic_to_latin_pashto:
            result += arabic_to_latin_pashto[text[i:i+2]]
            i += 2
        else:
            result += arabic_to_latin_pashto.get(text[i], text[i])
            i += 1
    return result

# Function to convert Latin-based script to Pashto script
def latin_to_pashto_script(text):
    result = ''
    i = 0
    while i < len(text):
        if i + 1 < len(text) and text[i:i+2] in latin_to_arabic_pashto:
            result += latin_to_arabic_pashto[text[i:i+2]]
            i += 2
        else:
            result += latin_to_arabic_pashto.get(text[i], text[i])
            i += 1
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

# Function to convert a file from Pashto script to Latin-based script and save it to another file
def convert_pashto_file_to_latin(input_file_path, output_file_path):
    pashto_text = read_text_file(input_file_path)
    latin_text = pashto_to_latin_script(pashto_text)
    write_text_file(output_file_path, latin_text)

# Function to convert a file from Latin-based script to Pashto script and save it to another file
def convert_latin_file_to_pashto(input_file_path, output_file_path):
    latin_text = read_text_file(input_file_path)
    pashto_text = latin_to_pashto_script(latin_text)
    write_text_file(output_file_path, pashto_text)

# Function to convert a file from Pashto script to Latin-based script and return the result as a variable
def convert_pashto_file_to_latin_variable(input_file_path):
    pashto_text = read_text_file(input_file_path)
    return pashto_to_latin_script(pashto_text)

# Function to convert a file from Latin-based script to Pashto script and return the result as a variable
def convert_latin_file_to_pashto_variable(input_file_path):
    latin_text = read_text_file(input_file_path)
    return latin_to_pashto_script(latin_text)

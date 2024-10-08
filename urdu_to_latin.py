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

    $FileInfo: urdu_to_latin.py - Last Update: 5/31/2024 Ver. 1.0.0 RC 1 - Author: joshuatp $
'''

import os

# Comprehensive conversion dictionaries for Urdu script
arabic_to_latin_urdu = {
    'ا': 'A', 'ب': 'B', 'پ': 'P', 'ت': 'T', 'ٹ': 'Ṭ', 'ث': 'S', 'ج': 'J', 'چ': 'Č', 'ح': 'H', 'خ': 'Kh', 'د': 'D',
    'ڈ': 'Ḍ', 'ذ': 'Z', 'ر': 'R', 'ڑ': 'Ṛ', 'ز': 'Z', 'ژ': 'Zh', 'س': 'S', 'ش': 'Sh', 'ص': 'Ṣ', 'ض': 'Ẓ', 'ط': 'Ṭ',
    'ظ': 'Ẓ', 'ع': 'ʿ', 'غ': 'Gh', 'ف': 'F', 'ق': 'Q', 'ک': 'K', 'گ': 'G', 'ل': 'L', 'م': 'M', 'ن': 'N', 'ں': 'Ṉ',
    'و': 'V', 'ہ': 'H', 'ھ': 'H', 'ء': "'", 'ی': 'Y', 'ے': 'E', 'ۓ': 'Ae', 'آ': 'Ā', ' ': ' ', '،': ',', '؟': '?',
    '؛': ';', '!': '!', '‌': ' ',  # ZWNJ replaced with space
    'ً': 'an', 'َ': 'a', 'ُ': 'u', 'ِ': 'i', 'ّ': '', 'ْ': '', 'ٔ': '', 'ٓ': '',
    'ئ': 'Y', 'ي': 'i', 'ك': 'K', 'ى': 'Y', '«': '"', '»': '"', '(': '(', ')': ')', '۱': '1', '۲': '2', '۳': '3',
    '۴': '4', '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9', '۰': '0', '.': '.', ':': ':', '—': '-',
    '\n': '\n', '\r': '\r', '[': '[', ']': ']'
}

latin_to_arabic_urdu = {v: k for k, v in arabic_to_latin_urdu.items()}

# Function to convert Urdu script to Latin-based script


def urdu_to_latin_script(text):
    result = ''
    for char in text:
        result += arabic_to_latin_urdu.get(char, char)
    return result

# Function to convert Latin-based script to Urdu script


def latin_to_urdu_script(text):
    result = ''
    for char in text:
        result += latin_to_arabic_urdu.get(char, char)
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

# Function to convert a file from Urdu script to Latin-based script and
# save it to another file


def convert_urdu_file_to_latin(input_file_path, output_file_path):
    urdu_text = read_text_file(input_file_path)
    latin_text = urdu_to_latin_script(urdu_text)
    write_text_file(output_file_path, latin_text)

# Function to convert a file from Latin-based script to Urdu script and
# save it to another file


def convert_latin_file_to_urdu(input_file_path, output_file_path):
    latin_text = read_text_file(input_file_path)
    urdu_text = latin_to_urdu_script(latin_text)
    write_text_file(output_file_path, urdu_text)

# Function to convert a file from Urdu script to Latin-based script and
# return the result as a variable


def convert_urdu_file_to_latin_variable(input_file_path):
    urdu_text = read_text_file(input_file_path)
    return urdu_to_latin_script(urdu_text)

# Function to convert a file from Latin-based script to Urdu script and
# return the result as a variable


def convert_latin_file_to_urdu_variable(input_file_path):
    latin_text = read_text_file(input_file_path)
    return latin_to_urdu_script(latin_text)

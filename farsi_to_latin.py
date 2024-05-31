import os

# Dictionaries for conversion
arabic_to_latin = {
    'ا': 'A', 'ب': 'B', 'پ': 'P', 'ت': 'T', 'ث': 'S', 'ج': 'J', 'چ': 'Č', 'ح': 'H', 'خ': 'Kh', 'د': 'D',
    'ذ': 'Z', 'ر': 'R', 'ز': 'Z', 'ژ': 'Ž', 'س': 'S', 'ش': 'Sh', 'ص': 'S', 'ض': 'Z', 'ط': 'T', 'ظ': 'Z',
    'ع': 'ʿ', 'غ': 'Gh', 'ف': 'F', 'ق': 'Q', 'ک': 'K', 'گ': 'G', 'ل': 'L', 'م': 'M', 'ن': 'N', 'و': 'V',
    'ه': 'H', 'ی': 'Y', 'آ': 'Ā', ' ': ' ', '،': ',', '؟': '?', '؛': ';', '!': '!'
}

latin_to_arabic = {v: k for k, v in arabic_to_latin.items()}

# Function to convert Arabic script to Latin-based script
def arabic_to_latin_script(text):
    result = ''
    for char in text:
        result += arabic_to_latin.get(char, char)
    return result

# Function to convert Latin-based script to Arabic script
def latin_to_arabic_script(text):
    result = ''
    i = 0
    while i < len(text):
        if i + 1 < len(text) and text[i:i+2] in latin_to_arabic:
            result += latin_to_arabic[text[i:i+2]]
            i += 2
        else:
            result += latin_to_arabic.get(text[i], text[i])
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

# Function to convert a file from Arabic script to Latin-based script and save it to another file
def convert_arabic_file_to_latin(input_file_path, output_file_path):
    arabic_text = read_text_file(input_file_path)
    latin_text = arabic_to_latin_script(arabic_text)
    write_text_file(output_file_path, latin_text)

# Function to convert a file from Latin-based script to Arabic script and save it to another file
def convert_latin_file_to_arabic(input_file_path, output_file_path):
    latin_text = read_text_file(input_file_path)
    arabic_text = latin_to_arabic_script(latin_text)
    write_text_file(output_file_path, arabic_text)

# Function to convert a file from Arabic script to Latin-based script and return the result as a variable
def convert_arabic_file_to_latin_variable(input_file_path):
    arabic_text = read_text_file(input_file_path)
    return arabic_to_latin_script(arabic_text)

# Function to convert a file from Latin-based script to Arabic script and return the result as a variable
def convert_latin_file_to_arabic_variable(input_file_path):
    latin_text = read_text_file(input_file_path)
    return latin_to_arabic_script(latin_text)

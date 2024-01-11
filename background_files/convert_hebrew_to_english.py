


def convert_hebrew_to_english(input_string:str):
    hebrew_to_english_mapping = {
        'א': 'a',
        'ב': 'b',
        'ג': 'g',
        'ד': 'd',
        'ה': 'h',
        'ו': 'v',
        'ז': 'z',
        'ח': 'kh',
        'ט': 't',
        'י': 'y',
        'כ': 'k',
        'ך': 'kh',  # Final form of כ
        'ל': 'l',
        'מ': 'm',
        'ם': 'm',  # Final form of מ
        'נ': 'n',
        'ן': 'n',  # Final form of נ
        'ס': 's',
        'ע': 'e',
        'פ': 'p',
        'ף': 'f',  # Final form of פ
        'צ': 'ts',
        'ץ': 'ts',  # Final form of צ
        'ק': 'k',
        'ר': 'r',
        'ש': 'sh',
        'ת': 't',
    }

    output_string = ''
    for char in input_string:
        if char.isalpha() and char.isascii():
            # If the character is an English letter, keep it unchanged
            output_string += char
        elif char.isdigit():
            # If the character is a digit, keep it unchanged
            output_string += char
        elif char in hebrew_to_english_mapping:
            # If the character is a Hebrew letter, apply the mapping
            output_string += hebrew_to_english_mapping[char]
        elif char == ',':
            continue
        elif char.isspace():
            output_string += '_'
        else:
            # Keep other characters unchanged
            output_string += char

    return output_string


def find_angel(filename):
    filenum = int(filename[4])
    angel = 10 + filenum * 10
    return str(angel)




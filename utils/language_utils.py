serbocroatian_cyrillic_letters = [
    'а', 'б', 'в', 'г', 'д', 'ђ', 'е', 'ж', 'з', 'и', 'ј', 'к', 'л', 'љ', 'м',
    'н', 'њ', 'о', 'п', 'р', 'с', 'т', 'ћ', 'у', 'ф', 'х', 'ц', 'ч', 'џ', 'ш',
    'А', 'Б', 'В', 'Г', 'Д', 'Ђ', 'Е', 'Ж', 'З', 'И', 'Ј', 'К', 'Л', 'Љ', 'М',
    'Н', 'Њ', 'О', 'П', 'Р', 'С', 'Т', 'Ћ', 'У', 'Ф', 'Х', 'Ц', 'Ч', 'Џ', 'Ш',
]

serbocroatian_latin_letters = [
    'a', 'b', 'v', 'g', 'd', 'đ', 'e', 'ž', 'z', 'i', 'j', 'k', 'l', 'lj', 'm',
    'n', 'nj', 'o', 'p', 'r', 's', 't', 'ć', 'u', 'f', 'h', 'c', 'č', 'dž', 'š',
    'A', 'B', 'V', 'G', 'D', 'Đ', 'E', 'Ž', 'Z', 'I', 'J', 'K', 'L', 'Lj', 'M',
    'N', 'Nj', 'O', 'P', 'R', 'S', 'T', 'Ć', 'U', 'F', 'H', 'C', 'Č', 'Dž', 'Š',
]


def serbocroatian_to_latin(text):
    """Converts Serbo-Croatian Cyrillic text to Latin script.
    Args:
        text (str): Serbo-Croatian text.
    Returns:
        str: Latin script.
    """
    # Replace all the Cyrillic letters with their Latin equivalents
    for cyrillic_letter, latin_letter in zip(serbocroatian_cyrillic_letters, serbocroatian_latin_letters):
        text = text.replace(cyrillic_letter, latin_letter)
    return text


def serbocroatian_to_cyrillic(text):
    """Converts Serbo-Croatian Latin text to Cyrillic script.
    Args:
        text (str): Serbo-Croatian text.
    Returns:
        str: Cyrillic script.
    """
    for cyrillic_letter, latin_letter in zip(serbocroatian_cyrillic_letters, serbocroatian_latin_letters):
        text = text.replace(latin_letter, cyrillic_letter)
    return text
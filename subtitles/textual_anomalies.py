MIN_LENGTH = 30

similar_groups = [
    [["a", "o", "u", "y", "e", "i"], 0.3],
    [["b", "c", "d", "f", "g", "h", "j", "k", "l", "m", "n", "p", "q", "r", "s", "t", "v", "w", "x", "z"], 0.2],
    [["i", "y"], 0.4],
    [["o", "u"], 0.2],
    [["a", "o"], 0.1],
    [["i", "e"], 0.2],
    [["b", "v"], 0.4],
    [["c", "k", "q"], 0.5],
    [["d", "t"], 0.4],
    [["p", "b"], 0.4],
    [["f", "v"], 0.4],
    [["g", "j"], 0.1],
    [["g", "k"], 0.4],
    [["g", "q"], 0.2],
    [["h", "x"], 0.2],
    [["h", "k"], 0.1],
    [["m", "n"], 0.5],
    [["l", "r"], 0.4],
    [["s", "z"], 0.4],
    [["s", "c"], 0.4],
]


def letter_change_cost(letter1, letter2):
    if letter1 == letter2:
        return 0
    similarity = 0
    for i in range(len(similar_groups)):
        if letter1 in similar_groups[i][0] and letter2 in similar_groups[i][0]:
            similarity += similar_groups[i][1]
    return 1 - similarity


def is_anomalous(text):
    if len(text) < MIN_LENGTH:
        return False
    else:
        for l in range(1, 7):
            folds = [text[i:i + l] for i in range(0, len(text), l)]
            folds_set = set(folds)
            if len(folds_set) <= 3:
                return True
        return False


def transliterate(input_str):
    cyrillic_to_latin = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
        'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i',
        'й': 'j', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
        'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
        'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch',
        'ш': 'sh', 'щ': 'shch', 'ъ': '', 'ы': 'y', 'ь': '',
        'э': 'e', 'ю': 'yu', 'я': 'ya'
    }
    is_cyrillic = False
    for char in input_str:
        if char in cyrillic_to_latin.keys():
            is_cyrillic = True
            break
    if is_cyrillic:
        output_str = ''
        for char in input_str:
            output_str += cyrillic_to_latin.get(char, char)
        return output_str
    return input_str


def phonetic_similarity(str1, str2):
    str1 = str1.lower()
    str2 = str2.lower()
    str1 = transliterate(str1)
    str2 = transliterate(str2)
    str1 = str1.replace(" ", "").replace(",", "").replace(".", "").replace("!", "").replace("?", "").replace(":", "").replace(";", "")
    str2 = str2.replace(" ", "").replace(",", "").replace(".", "").replace("!", "").replace("?", "").replace(":", "").replace(";", "")

    d = {}
    lenstr1 = len(str1)
    lenstr2 = len(str2)
    for i in range(-1, lenstr1 + 1):
        d[(i, -1)] = i + 1
    for j in range(-1, lenstr2 + 1):
        d[(-1, j)] = j + 1

    for i in range(lenstr1):
        for j in range(lenstr2):
            cost = letter_change_cost(str1[i], str2[j])
            d[(i, j)] = min(
                d[(i - 1, j)] + 1,
                d[(i, j - 1)] + 1,
                d[(i - 1, j - 1)] + cost,
            )

            """
            if i and j and str1[i] == str2[j - 1] and str1[i - 1] == str2[j]:
                d[(i, j)] = min(d[(i, j)], d[i - 2, j - 2] + cost)
            """

    dist = d[lenstr1 - 1, lenstr2 - 1]
    similarity = 1 - dist / max(lenstr1, lenstr2)
    return similarity


if __name__ == "__main__":
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    for letter1 in alphabet:
        for letter2 in alphabet:
            print(f"{letter1}-{letter2}: {letter_change_cost(letter1, letter2)}")

    print(phonetic_similarity("hui", "hiu"))
    exit(0)

    texts = [
        "Hello, world!",
        "Hello, world!Hello, world!",
        "AHAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
        "ding-dong-ding-ding-ding-ding-ding-ding-ding-ding-ding-ding-ding",
        "dfkjdfgfkjfgkjgflkfgfg",
        "aha-aha-aha-aha-aha-aha-aha-aha-aha-aha-aha-aha-aha-aha-aha-aha-aha-aha-aha-aha-aha-aha-aha-aha"
    ]
    assert not is_anomalous(texts[0])
    assert not is_anomalous(texts[1])
    assert is_anomalous(texts[2])
    assert is_anomalous(texts[3])
    assert not is_anomalous(texts[4])
    assert is_anomalous(texts[5])

"""
write a Python function that will check if the string mostly contains of repeating pattern
here are some tests the algorithm should pass
texts = [
        "Hello, world!",
        "Hello, world!Hello, world!",
        "AHAAAAAAAAAAAAAAAAAAAAAAAA",
        "ding-dong=ding-ding-ding-ding-ding-ding-ding",
        "dfkjdfgfkjfgkjgflkfgfg",
        "aha-aha-aha-aha-aha-aha-aha-aha"
    ]
    assert not is_anomalous(texts[0])
    assert not is_anomalous(texts[1])
    assert is_anomalous(texts[2])
    assert is_anomalous(texts[3])
    assert not is_anomalous(texts[4])
    assert is_anomalous(texts[5])
"""

import fasttext
import translation.MarianTranslator as MarianTranslator
import os

ft_model = fasttext.load_model('models//lid.176.ftz')


def detect_language(message):
    message = message.replace("\n", "")
    res = ft_model.predict(message, k=10)
    lang = res[0][0][len("__label__"):]
    if lang in ["hr", "sr", "bs", 'sh']:
        lang = "hr"
    return lang


def to_english(message):
    translator = MarianTranslator.MarianTranslator()
    language = detect_language(message)

    """
    supported_langs = [
        'ko',
        'tr',
        'lt',
        'lv',
        'it',
        'hu',
        'he',
        'sh',
        'fr',
        'et',
        'el',
        'bg',
        'ar',
        'fi',
        'zh',
        'vi',
        'uk',
        'sv',
        'sk',
        'ru',
        'pl',
        'nl',
        'mk',
        'de',
        'cs',
        'ja',
        'es'
    ]
    """

    supported_langs = [
        'es', 'ja', 'de', 'nl', 'ru', 'zh', 'ar', 'fr', 'it', 'ko', 'tr', 'po'
    ]

    if language == "en" or language not in supported_langs:
        return message
    else:
        translator.load_model(language, "en")
        return translator.translate(message, language, "en")

if __name__ == "__main__":
    print(to_english("Как тебя зовут?"))

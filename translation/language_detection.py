import fasttext
import translation.MarianTranslator as MarianTranslator
import os

ft_model = fasttext.load_model('models//lid.176.ftz')


def detect_language(message):
    message = message.replace("\n", "")
    res = ft_model.predict(message, k=10)
    lang = res[0][0][len("__label__"):]
    return lang


def to_english(message):
    translator = MarianTranslator.MarianTranslator()
    language = detect_language(message)
    if language == "en" or language not in ['es', 'fr', 'de', 'it', 'pt', 'ru', 'ar', 'zh', 'ja', 'ko', 'pl', 'tr']:
        return message
    else:
        translator.load_model(language, "en")
        return translator.translate(message, language, "en")

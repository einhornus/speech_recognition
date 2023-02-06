import subtitles
import youtube.download
import translation.MarianTranslator
import translation.MultiTranslator
import translation.translate_subs
import storage.catalogue
import subtitles.subs


def parse_languages_required(languages_required_string):
    if languages_required_string == "og":
        return ["og", "en"]
    if len(languages_required_string) == 2:
        if languages_required_string == "en":
            return ["og", "en"]
        return ["og", "en", languages_required_string]
    if len(languages_required_string) == 5:
        languages_required_string = languages_required_string.split("_")[1]
        if languages_required_string == "en":
            return ["og", "en"]
        else:
            return ["og", "en", languages_required_string]


def meet_requirement(id, detected_language, language_required):
    actual_language_required = language_required
    if language_required == "og":
        actual_language_required = detected_language

    presult = storage.catalogue.Catalogue.get_subtitles(id, actual_language_required)
    if presult is not None:
        return presult, actual_language_required

    pulled_subs = youtube.download.pull_subs(id, actual_language_required, only_manual=True)
    if pulled_subs is not None:
        return pulled_subs, actual_language_required
    else:
        if actual_language_required == detected_language:
            gensub = subtitles.generation_core.generate_subtitles("data//youtube//_media.mp4",
                                                                  language=detected_language,
                                                                  task="transcribe")
            return gensub, actual_language_required
        else:
            if actual_language_required == "en":
                eng_gensub = subtitles.generation_core.generate_subtitles("data//youtube//_media.mp4",
                                                                          language="en",
                                                                          task="translate")
                return eng_gensub, actual_language_required
            else:
                eng_subs = storage.catalogue.Catalogue.get_subtitles(id, "en")
                translator = translation.MarianTranslator.MarianTranslator()
                model_loaded = translator.load_model("en", actual_language_required)
                trans_data = translation.translate_subs.just_translate(translator, eng_subs,
                                                                       "en", actual_language_required)
                trans_subs = subtitles.subs.Subtitles(data=trans_data)
                return trans_subs, actual_language_required

import subtitles
import youtube.download
import translation.MarianTranslator
import translation.MultiTranslator
import translation.translate_subs

def produce_requirements(id, language):
    file_name = "data//youtube//" + id
    file_name += "_"
    requirements = []
    translation_language = None
    if language == "og":
        requirements.append(file_name + "og.srt")
    if language != "og" and len(language) == 2:
        requirements.append(file_name + "og" + ".srt")
        requirements.append(file_name + language + ".srt")
        translation_language = language
    if len(language) == 5:
        lang = language.split("_")[1]
        requirements.append(file_name + "og" + ".srt")
        requirements.append(file_name + lang + ".srt")
        translation_language = lang
    if len(language) > 5:
        lang = language.split("_")[1]
        requirements.append(file_name + "og" + ".srt")
        requirements.append(file_name + lang + ".srt")
        requirements.append(file_name + lang + "_hi" + ".srt")
        translation_language = lang
    return requirements, translation_language

def meet_requirement_og(obj, detected_language):
    pulled_subs = youtube.download.pull_subs(obj["link"], detected_language, only_manual=True)
    if pulled_subs is not None:
        gensub = pulled_subs
    else:
        gensub = subtitles.generation_core.generate_subtitles("data//youtube//_media.mp4",
                                                              language=detected_language,
                                                              task="transcribe")
    return gensub


def meet_requirement_translation(obj, detected_language, requirement):
    lang = requirement.replace(".srt", "").split("_")[-1]

    if detected_language == lang:
        return subtitles.subs.Subtitles(file = requirement.replace("_"+lang, "_og"))


    gensub = subtitles.subs.Subtitles(file=requirement.replace(lang, "og"))
    trans_sub = None
    pulled_subs = youtube.download.pull_subs(obj["link"], lang)
    if pulled_subs is not None:
        trans_sub = pulled_subs
    else:
        if lang == "en" and detected_language != "en":
            trans_sub = subtitles.generation_core.generate_subtitles(
                "data//youtube//_media.mp4",
                language='en',
                task="translate")
        else:
            translator = translation.MarianTranslator.MarianTranslator()
            model_loaded = translator.load_model(detected_language, lang)
            if model_loaded:
                new_tran = translation.translate_subs.just_translate(translator, gensub,
                                                                     detected_language, lang)
                trans_sub = subtitles.subs.Subtitles()
                trans_sub.data = new_tran
            else:
                trans_sub = subtitles.generation_core.generate_subtitles(
                    "data//youtube//_media.mp4",
                    language='en',
                    task="translate")
                model_loaded = translator.load_model('en', lang)
                new_tran = translation.translate_subs.just_translate(translator, trans_sub,
                                                                     'en', lang)
                trans_sub = subtitles.subs.Subtitles()
                trans_sub.data = new_tran
    return trans_sub


def translate_to_english(obj, detected_language, requirements):
    save_file = requirements[0].replace("_og.srt", "_en.srt")
    if detected_language == "en":
        eng_subs = subtitles.subs.Subtitles(file=requirements[0])
        eng_subs.save(save_file)
        return save_file
    else:
        for i in range(len(requirements)):
            if requirements[i].endswith("_en.srt"):
                return save_file
        trans_sub = subtitles.generation_core.generate_subtitles(
            "data//youtube//_media.mp4",
            language='en',
            task="translate")
        trans_sub.save(save_file)
        return save_file


def meet_requirement(obj, requirement, detected_language):
    subs = None
    if requirement.endswith("_og.srt"):
        subs = meet_requirement_og(obj, detected_language)
    else:
        subs = meet_requirement_translation(obj, detected_language, requirement)
    subs.save(requirement)

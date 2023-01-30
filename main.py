import whisper
import time
import utils.language_utils
import json
import os
import subtitles.subs
import generate_subtitles
import youtube.download as youtube

def parse_folder(folder, language=None):
    res = {}
    meta_obj = json.load(open("data//content//" + folder + "//meta.json", "r", encoding="utf-8"))
    language = meta_obj["language"]
    files_list = os.listdir("data//content//" + folder)
    res["language"] = language
    res["guide"] = None
    for i in range(len(files_list)):
        if files_list[i].endswith(".wav") or files_list[i].endswith(".mp3") or files_list[i].endswith(".mp4") or files_list[i].endswith(".mkv"):
            res["media"] = "data//content//" + folder + "//" + files_list[i]
        if files_list[i] == "guide.txt":
            res["guide"] = "data//content//" + folder + "//" + files_list[i]
    return res


def generate_subs(folder, model="large", _language=None):
    obj = parse_folder(folder)
    language = obj["language"]
    if _language is not None:
        language = _language
    media = obj["media"]
    generate_subtitles.generate_subtitles(media, language, model=model)


if __name__ == "__main__":
    #generate_subs("Russian//Music//Frozen, Let it go")
    #generate_subs("Serbian//Music//Frozen, Let it go")
    #generate_subs("Serbian//Cartoons//Urfin Jus")

    #generate_subs("Russian//Redroom//Karansebesh")
    #generate_subs("English//Bill Wurtz//History of the entire world")
    #generate_subs("Russian//Series//Interny//S1E1")
    #generate_subs("Russian//Linguistics//Правильный язык на протяжении истории")

    #youtube.download("https://www.youtube.com/watch?v=S-Pcg8qR8-g")
    pass

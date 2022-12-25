import whisper
import time
import utils.language_utils
import json
import os
import subtitles.subtitles
import generate_subtitles

def parse_folder(folder):
    res = {}
    meta_obj = json.load(open("data//content//" + folder + "//meta.json", "r"))
    language = meta_obj["language"]
    files_list = os.listdir("data//content//" + folder)
    res["language"] = language
    res["guide"] = None
    for i in range(len(files_list)):
        if files_list[i].endswith(".wav") or files_list[i].endswith(".mp3") or files_list[i].endswith(".mp4"):
            res["media"] = "data//content//" + folder + "//" + files_list[i]
        if files_list[i] == "guide.txt":
            res["guide"] = "data//content//" + folder + "//" + files_list[i]
    return res


def generate_subs(folder, model="medium.en"):
    obj = parse_folder(folder)
    language = obj["language"]
    media = obj["media"]
    generate_subtitles.generate_subtitles(media, language, model=model)


if __name__ == "__main__":
    generate_subs("English//Bill Wurtz//History of the entire world")

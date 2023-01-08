from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from os import listdir
import random
import string
import os
import json
import subtitles.subtitles
from fastapi import BackgroundTasks, FastAPI
import time
import asyncio
from collections import deque
import youtube.utils
import youtube.download
import generate_subtitles
import translation.translate_subs
import translation.MultiTranslator
import translation.MarianTranslator

is_debug = False

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

q = []


def boot():
    for i in range(len(q)):
        if q[i]["status"] == "generating":
            return

    while len(q) > 0:
        if q[0]["status"] == "pending":
            obj = q[0]
            obj["status"] = "generating"
            obj["time_start"] = time.time()
            print("Generating " + obj["link"] + " " + obj["language"])
            youtube.download.download(obj["link"])
            print("Downloaded", obj["link"])
            detected_language = generate_subtitles.detect_language("data//youtube//___media.mp4")
            # if obj["language"] == "og":
            if obj["language"] == 'en':
                gensub = generate_subtitles.generate_subtitles("data//youtube//___media.mp4",
                                                               language='en',
                                                               task="translate")
                meta_obj = {"language": obj["language"], "original_language": detected_language}
                json.dump(meta_obj, open(obj["meta_file_name2"], "w", encoding="utf-8"))
                gensub.save(obj["srt_file_name2"])
            else:
                gensub = generate_subtitles.generate_subtitles("data//youtube//___media.mp4", language=detected_language,
                                                                  task="transcribe")
                meta_obj = {"language": detected_language}
                json.dump(meta_obj, open(obj["meta_file_name"], "w", encoding="utf-8"))
                gensub.save(obj["srt_file_name"])

                if obj["language"] != "og":
                    translator = translation.MarianTranslator.MarianTranslator()
                    translator.load_model(detected_language, obj["language"])
                    new_tran = translation.translate_subs.just_translate(translator, gensub, detected_language, obj["language"])
                    new_subs = subtitles.subtitles.Subtitles()
                    new_subs.data = new_tran
                    new_name = obj["srt_file_name"].replace("og.srt", obj["language"] + ".srt")
                    new_subs.save(new_name)

                    meta_obj = {"language": obj["language"], "original_language": detected_language}
                    json.dump(meta_obj, open(obj["meta_file_name2"], "w", encoding="utf-8"))

            print("Subtitles generated")
            q.remove(obj)


def set_prior_queue(res, link, language):
    is_generating = False
    current_time = time.time()
    time_generating = -1
    for item in q:
        if item["status"] == "generating" and item["link"] == link and item["language"] == language:
            is_generating = True
            time_generating = current_time - item["time_start"]
            break
    # res["queue"] = q
    res["time_generating"] = 0
    res["is_generating"] = is_generating
    if is_generating:
        res["time_generating"] = time_generating
    res["prior_queue"] = []
    for item in q:
        if item["link"] == link and item["language"] == language:
            res["item"] = item
            res["item"]["time_generating"] = time_generating
            break
        res["prior_queue"].append(item)
        if item["status"] == "generating":
            item["time_generating"] = current_time - item["time_start"]

@app.get("/subtitles")
async def request(background_tasks: BackgroundTasks, id: str, language: str = "og"):
    file_name = "data//youtube//" + id
    file_name += "_"
    meta_file_name = file_name+"og.json"
    srt_file_name = file_name+"og.srt"

    srt_file_name2 = None
    meta_file_name2 = None

    if language != "og":
        meta_file_name2 = srt_file_name.replace("og.srt", language + ".json")
        srt_file_name2 = srt_file_name.replace("og.srt", language + ".srt")

    already_exists = os.path.exists(srt_file_name)
    if language != "og":
        already_exists = os.path.exists(srt_file_name2)

    if not already_exists:
        que_obj = {}
        found = False
        for item in q:
            if item["link"] == id and item["language"] == language:
                found = True
                que_obj = item.copy()
        if not found:
            res = {}
            que_obj["link"] = id
            que_obj["language"] = language
            que_obj["duration"] = youtube.utils.get_duration(id)
            que_obj["meta_file_name"] = meta_file_name
            que_obj["srt_file_name"] = srt_file_name
            que_obj["meta_file_name2"] = meta_file_name2
            que_obj["srt_file_name2"] = srt_file_name2
            que_obj["status"] = "pending"
            que_obj["time_add"] = time.time()
            q.append(que_obj)
            background_tasks.add_task(boot)
            res["status"] = "in_queue"
            set_prior_queue(res, id, language)
            if len(q) == 1:
                res["is_generating"] = True
                res["item"] = que_obj
                res["time_generating"] = 0
            return res
        else:
            res = {}
            res["status"] = "in_queue"
            set_prior_queue(res, id, language)
            background_tasks.add_task(boot)
            return res
    else:
        if language == "og":
            res = json.load(open(meta_file_name, "r", encoding="utf-8"))
            subs = subtitles.subtitles.Subtitles(file=srt_file_name)
            res["subtitles"] = []
            for i in range(len(subs.data)):
                res["subtitles"].append(subs.data[i])
            res["status"] = "done"
        else:
            res = json.load(open(meta_file_name2, "r", encoding="utf-8"))
            subs = subtitles.subtitles.Subtitles(file=srt_file_name2)
            res["subtitles"] = []
            for i in range(len(subs.data)):
                res["subtitles"].append(subs.data[i])
            res["status"] = "done"
        background_tasks.add_task(boot)
        return res


if __name__ == "__main__":
    uvicorn.run("server:app", debug=True, reload=True, host="0.0.0.0", port=8009)

    """
    t = translation.MarianTranslator.MarianTranslator()
    t.load_model("ru", "en")
    subs = subtitles.subtitles.Subtitles(file="data//test.srt")
    res = translation.translate_subs.just_translate(t, subs, "ru", "en")
    new_subs = subtitles.subtitles.Subtitles()
    new_subs.data = res

    new_subs.save("data//test2.srt")
    print(res)
    """



"""
как учили писать и читать
http://164.90.201.98/?videoId=d9rrz9X-ocI&language=en
http://164.90.201.98/?videoId=d9rrz9X-ocI&language=og

нгемо ндонг
http://164.90.201.98/?videoId=0cLWSa0ABBM&language=en
http://164.90.201.98/?videoId=0cLWSa0ABBM&language=og

лежеюокер уснул на уроке
http://164.90.201.98/?videoId=2i3u8VJjzBQ&language=og
http://164.90.201.98/?videoId=2i3u8VJjzBQ&language=en

  папаньки 1.1
  http://164.90.201.98/?videoId=nE9UaU3eZDc&language=og
  http://164.90.201.98/?videoId=nE9UaU3eZDc&language=en
  
history of the entire world, i guess
http://164.90.201.98/?videoId=xuCn8ux2gbs&language=og

nimfa ili tigrica
http://164.90.201.98/?videoId=p5FHYqu_r1I&language=en
http://164.90.201.98/?videoId=p5FHYqu_r1I&language=og
"""
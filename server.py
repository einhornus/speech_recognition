import sqlite3

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
import storage.catalogue
import storage.video
import storage.search

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
catalogue = storage.catalogue.Catalogue()

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

            detected_language = generate_subtitles.detect_language("data//youtube//___media.mp4")
            for requirement in obj["requirements"]:
                if not os.path.exists(requirement):
                    if requirement.endswith("_og.srt"):
                        gensub = generate_subtitles.generate_subtitles("data//youtube//___media.mp4",
                                                                       language=detected_language,
                                                                       task="transcribe")
                        gensub.save(requirement)
                    else:
                        if requirement.endswith(".srt"):
                            lang = requirement.replace(".srt", "").split("_")[-1]
                            gensub = subtitles.subtitles.Subtitles(file=requirement.replace(lang, "og"))
                            trans_sub = None
                            if lang == "en" and detected_language != "en":
                                trans_sub = generate_subtitles.generate_subtitles("data//youtube//___media.mp4",
                                                                                  language='en',
                                                                                  task="translate")
                            else:
                                translator = translation.MarianTranslator.MarianTranslator()
                                translator.load_model(detected_language, lang)
                                new_tran = translation.translate_subs.just_translate(translator, gensub,
                                                                                     detected_language, lang)
                                trans_sub = subtitles.subtitles.Subtitles()
                                trans_sub.data = new_tran
                            trans_sub.save(requirement)

            id = obj["link"]
            original_language = detected_language
            language = obj["language"]
            title = obj["title"]
            description = obj["description"]
            publish_date = obj["publish_date"]
            thumbnail = obj["thumbnail"]
            keywords = obj["keywords"]
            duration = obj["duration"]
            english_subs = obj["requirements"][-1]
            content_subs = subtitles.subtitles.Subtitles(file=english_subs)
            content = content_subs.get_content()
            video = storage.video.Video(
                id=id,
                original_language=original_language,
                language=language,
                title=title,
                description=description,
                thumbnail=thumbnail,
                keywords=keywords,
                duration=duration,
                content=content
            )
            catalogue.add_video(video)

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


@app.get("/search")
async def search(query: str, language: str, original_language: str):
    res = storage.search.search_catalogue(query, catalogue, language=language, original_language=original_language)
    return res


@app.get("/subtitles")
async def request(background_tasks: BackgroundTasks, id: str, language: str = "og"):
    file_name = "data//youtube//" + id
    file_name += "_"
    meta_file_name = file_name + ".json"
    srt_file_name = file_name + "og.srt"

    requirements = []
    if language == "og":
        requirements.append(file_name + "og.srt")
        requirements.append(file_name + "en" + ".srt")
    if language != "og" and len(language) == 2:
        requirements.append(file_name + "og" + ".srt")
        requirements.append(file_name + language + ".srt")
        if language != "en":
            requirements.append(file_name + "en" + ".srt")
    if len(language) == 5:
        lang = language.split("_")[1]
        requirements.append(file_name + "og" + ".srt")
        requirements.append(file_name + lang + ".srt")
        if lang != "en":
            requirements.append(file_name + "en" + ".srt")
    if len(language) > 5:
        lang = language.split("_")[1]
        requirements.append(file_name + "og" + ".srt")
        requirements.append(file_name + lang + ".srt")
        requirements.append(file_name + lang + "_hi" + ".srt")
        if lang != "en":
            requirements.append(file_name + "en" + ".srt")

    remaining_requirements = []
    for requirement in requirements:
        if not os.path.exists(requirement):
            remaining_requirements.append(requirement)

    if len(remaining_requirements) > 0:
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
            youtube.utils.get_attributes(que_obj)
            que_obj["requirements"] = requirements
            que_obj["meta_file_name"] = meta_file_name
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
        if len(language) == 2:
            res = {}
            srt_file_name = requirements[-1]
            subs = subtitles.subtitles.Subtitles(file=srt_file_name)
            res["subtitles"] = []
            for i in range(len(subs.data)):
                res["subtitles"].append(subs.data[i])
            res["status"] = "done"
            if language == "og":
                res["type"] = "singular_og"
            else:
                res["type"] = "singular_translation"
        if len(language) == 5:
            res = {}
            original_subs = requirements[0]
            language_subs = requirements[1]
            subs1 = subtitles.subtitles.Subtitles(file=original_subs)
            subs2 = subtitles.subtitles.Subtitles(file=language_subs)
            res["original"] = []
            for i in range(len(subs1.data)):
                res["original"].append(subs1.data[i])
            res["translation"] = []
            for i in range(len(subs2.data)):
                res["translation"].append(subs2.data[i])
            res["status"] = "done"
            res["type"] = "dual"
        background_tasks.add_task(boot)
        return res


if __name__ == "__main__":
    uvicorn.run("server:app", debug=True, reload=False, host="0.0.0.0", port=8009)

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
как на Руси учили писать и читать
http://164.90.201.98/?videoId=d9rrz9X-ocI&language=en
http://164.90.201.98/?videoId=d9rrz9X-ocI&language=og

нгемо ндонг
http://164.90.201.98/?videoId=0cLWSa0ABBM&language=en
http://164.90.201.98/?videoId=0cLWSa0ABBM&language=og

лежебокер уснул на уроке
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

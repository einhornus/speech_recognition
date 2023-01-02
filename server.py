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

is_debug = False

app = FastAPI()
origins = ["*"]
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
            youtube.download.download(obj["link"])
            print("Downloaded", obj["link"])
            subtitles = generate_subtitles.generate_subtitles("data//youtube//___media.mp4", language="en")
            subtitles.save(obj["srt_file_name"])
            meta_obj = {"language": "en"}
            json.dump(meta_obj, open(obj["meta_file_name"], "w", encoding="utf-8"))
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
    res["is_generating"] = is_generating
    if is_generating:
        res["time_generating"] = time_generating
    res["prior_queue"] = []
    for item in q:
        if item["link"] == link and item["language"] == language:
            res["item"] = item
            break
        res["prior_queue"].append(item)
        if item["status"] == "generating":
            item["time_generating"] = current_time - item["time_start"]


@app.get("/request")
async def request(background_tasks: BackgroundTasks, link: str, language: str = "original"):
    file_name = "data//youtube//" + youtube.utils.get_id(link)
    file_name += "_" + language
    meta_file_name = file_name + ".json"
    srt_file_name = file_name + ".srt"
    if not os.path.exists(srt_file_name):
        que_obj = {}
        found = False
        for item in q:
            if item["link"] == link and item["language"] == language:
                found = True
                que_obj = item.copy()
        if not found:
            res = {}
            que_obj["link"] = link
            que_obj["language"] = language
            que_obj["size"] = youtube.utils.get_size(link)
            que_obj["meta_file_name"] = meta_file_name
            que_obj["srt_file_name"] = srt_file_name
            que_obj["status"] = "pending"
            que_obj["time_add"] = time.time()
            q.append(que_obj)
            background_tasks.add_task(boot)
            res["status"] = "in_queue"
            set_prior_queue(res, link, language)
            if len(q) == 1:
                res["is_generating"] = True
                res["item"] = que_obj
                res["time_generating"] = 0
            return res
        else:
            res = {}
            res["status"] = "in_queue"
            set_prior_queue(res, link, language)
            background_tasks.add_task(boot)
            return res
    else:
        res = json.load(open(meta_file_name, "r", encoding="utf-8"))
        subs = subtitles.subtitles.Subtitles(file=srt_file_name)
        res["subtitles"] = []
        for i in range(len(subs.data)):
            res["subtitles"].append(subs.data[i])
        res["status"] = "done"
        background_tasks.add_task(boot)
        return res


if __name__ == "__main__":
    uvicorn.run("server:app", debug=True, reload=True, host="0.0.0.0", port=8009, workers=1)

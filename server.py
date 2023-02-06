from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import subtitles.subs
from fastapi import BackgroundTasks, FastAPI
import time
import youtube.utils
import youtube.download
import subtitles.generation_core
import subtitles.synchronize
import translation.translate_subs
import translation.MultiTranslator
import translation.MarianTranslator
import storage.catalogue
import server_core.requirements

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

            detected_language = subtitles.generation_core.detect_language("data//youtube//_media.mp4")

            languages_required = obj["remaining_requirements"]
            for language in languages_required:
                subs, actual_language_required = server_core.requirements.meet_requirement(obj["link"],
                                                                                           detected_language, language)
                content = subs.get_content()
                storage.catalogue.Catalogue.write_subtitles(obj["link"], actual_language_required, content)

            video_exists = catalogue.is_video_exists(obj["link"])
            if not video_exists:
                english_content = storage.catalogue.Catalogue.get_subtitles(obj["link"], "en").get_raw_content()
                video_id = obj["link"]
                original_language = detected_language
                title = obj["title"]
                thumbnail = obj["thumbnail"]
                duration = obj["duration"]
                keywords = obj["keywords"]
                catalogue.add_video(video_id, title, english_content, keywords, thumbnail, duration,
                                    original_language, False)
                print("Subtitles generated")
            update_languages(obj["link"])
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
async def search(query: str, language: str, original_language: str, number_of_results:int):
    res = catalogue.search(query, language=language, original_language=original_language, number_of_results=number_of_results)
    return res


def try_pull_subs(id, requirements):
    for requirement in requirements:
        if not os.path.exists(requirement):
            language = requirement.replace(".srt", "").split("_")[-1]
            pulled_subs = youtube.download.pull_subs(id, language)
            if pulled_subs is not None:
                pulled_subs.save(requirement)


@app.get("/subtitles")
async def request(background_tasks: BackgroundTasks, id: str, language: str = "og"):
    languages_required = server_core.requirements.parse_languages_required(language)

    remaining_requirements = []
    for requirement in languages_required:
        if catalogue.get_subtitles(id, requirement) is None:
            remaining_requirements.append(requirement)
    # try_pull_subs(id, reqs)

    if len(remaining_requirements) > 0:
        que_obj = {}
        found = False
        for item in q:
            if item["link"] == id and item["language"] == language:
                found = True
                que_obj = item.copy()
        # found = False
        if not found:
            res = {}
            que_obj["link"] = id
            que_obj["language"] = language
            youtube.utils.get_attributes(que_obj)
            que_obj["remaining_requirements"] = remaining_requirements
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
            subs = catalogue.get_subtitles(id, language)
            subs = subtitles.synchronize.split_subs_timely(subs)
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
            subs1 = catalogue.get_subtitles(id, languages_required[0])
            subs2 = catalogue.get_subtitles(id, languages_required[-1])
            subs1, subs2 = subtitles.synchronize.sync_subs(subs1, subs2)
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
    lang = 'no'
    t.load_model("en", lang)
    subs = subtitles.subs.Subtitles(file="data//temp.srt")
    res = translation.translate_subs.just_translate(t, subs, "en", lang)
    new_subs = subtitles.subs.Subtitles()
    new_subs.data = res

    new_subs.save("data//temp2.srt")
    print(res)
    """

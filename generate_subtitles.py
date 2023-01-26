import whisper
import subtitles.subtitles
import utils.language_utils
import time
from scipy.io.wavfile import write
import numpy as np
import matplotlib.pyplot as plt

whisper_models = {}

DEFAULT_MODEL = "large"
backup_models = ["large", "medium"]
#backup_models_en = ["large", "medium", "small", "tiny", "medium.en", "small.en", "tiny.en"]
backup_models_en = ["large", "medium", "small", "medium.en"]

# backup_models = ["large", "small", "tiny"]
# backup_models_en = ["large", "small", "tiny", "medium.en", "small.en", "tiny.en"]


LIMIT = -0.6


def get_intervals_below_threshold(x, threshold):
    intervals = []
    start = None
    for i in range(len(x)):
        if x[i][0] < threshold:
            if start is None:
                start = (x[i][1], i)
        else:
            if start is not None:
                intervals.append((start, (x[i][1], i - 1)))
                start = None
    if start is not None:
        intervals.append((start, (x[-1][2], len(x) - 1)))
    return intervals


def merge(old_subs, start_time, end_time, new_subs):
    res_subs = []
    for i in range(len(old_subs)):
        if old_subs[i]["to"] <= start_time:
            res_subs.append(old_subs[i])
        else:
            break
    for i in range(len(new_subs)):
        line = new_subs[i]
        line["from"] += start_time
        line["to"] += start_time
        res_subs.append(line)
    for i in range(len(old_subs)):
        if old_subs[i]["from"] > end_time:
            res_subs.append(old_subs[i])
    return res_subs


def generate_subtitles(media, language, model=DEFAULT_MODEL, task="transcribe", t=None, rec=0, prompt=None):
    if model not in whisper_models:
        m = whisper.load_model(model, download_root="models")
        whisper_models[model] = m
    model = whisper_models[model]
    subtiles_name = media.replace(".wav", ".srt").replace(".mp3", ".srt").replace(".mp4", ".srt").replace(".mkv",
                                                                                                          ".srt")

    initial_media = media
    if t is not None:
        media = whisper.load_audio(media, sr=16000)
        media = media[t[0] * 16:t[1] * 16]
        # write("data//temp.wav", 16000, media)

    t1 = time.time()
    if prompt is None:
        res = model.transcribe(media, verbose=True, language=language, task=task, temperature=0.0,
                               condition_on_previous_text=False)
    else:
        res = model.transcribe(media, verbose=True, language=language, task=task, temperature=0.0,
                               condition_on_previous_text=False, prompt=prompt)
    t2 = time.time()
    print("Transcription time: " + str(t2 - t1))
    s = subtitles.subtitles.Subtitles()

    chart = []

    for i in range(len(res["segments"])):
        start = int(res["segments"][i]["start"] * 1000)
        end = int(res["segments"][i]["end"] * 1000)
        text = res["segments"][i]["text"]
        if language == "sr" or language == "hr":
            text = utils.language_utils.serbocroatian_to_cyrillic(text)
        line = {"from": start, "to": end, "text": text, "logprob": res["segments"][i]["avg_logprob"]}
        print(res["segments"][i]["text"], res["segments"][i]["avg_logprob"])
        chart.append((res["segments"][i]["avg_logprob"], start, end))
        s.data.append(line)

    intervals = get_intervals_below_threshold(chart, LIMIT)
    if rec == 0 and len(intervals) > 0:
        merged_res = s.data
        for interval in intervals:
            start_time = interval[0][0]
            end_time = interval[1][0]
            start_sub = interval[0][1]
            end_sub = interval[1][1]

            prompt = ""
            index = start_sub - 1
            if start_sub > 0:
                while index >= 0:
                    if len(prompt) > 200 or (("." in s.data[index]["text"]) and len(prompt) > 0):
                        break
                    prompt = s.data[index]["text"] + prompt
                    index -= 1

            if end_time - start_time > 5000 and end_sub + 1 - start_sub >= 2:
                average_logprob_before = s.get_average_logprob((start_sub, end_sub))

                lst = []
                _backup_models = backup_models_en if (language == "en" and task == "transcribe") else backup_models

                print("before", average_logprob_before)
                for backup_model in _backup_models:
                    new_subs = generate_subtitles(initial_media, language, backup_model, task, t=(start_time, end_time),
                                                  rec=rec + 1, prompt=prompt)
                    average_logprob_after = new_subs.get_average_logprob()
                    lst.append((average_logprob_after, new_subs, backup_model))
                lst.sort(key=lambda x: x[0], reverse=True)
                print("after")
                print(lst)

                average_logprob_after = lst[0][0]
                new_subs = lst[0][1]

                if average_logprob_after > average_logprob_before:
                    merged_res = merge(merged_res, start_time, end_time, new_subs.data)
                    print()
        s.data = merged_res
    s.save(subtiles_name)
    return s


def detect_language(media, model=DEFAULT_MODEL):
    audio = whisper.load_audio(media)
    audio = whisper.pad_or_trim(audio)
    mel = whisper.log_mel_spectrogram(audio)

    if model not in whisper_models:
        m = whisper.load_model(model, download_root="models")
        whisper_models[model] = m

    model = whisper_models[model]
    _, probs = model.detect_language(mel)
    detected_lang = max(probs, key=probs.get)

    if detected_lang in ["sr", "bs", "cnr"]:
        detected_lang = "hr"

    print("Detected language: " + detected_lang)
    return detected_lang


if __name__ == "__main__":
    # s = generate_subtitles("data//youtube//___media.mp4", 'en', t=((8*60+35)*1000, (12*60+15)*1000))
    # s = generate_subtitles("data//youtube//___media.mp4", 'en', t=(10*60+25, 11*60+20))
    s = generate_subtitles("data//youtube//___media.mp4", 'en')

    # s.save("data//temp.srt")

    text = ""
    for i in range(len(s.data)):
        text += s.data[i]["text"]
    print(text)

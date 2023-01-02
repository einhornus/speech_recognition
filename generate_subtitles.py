import whisper
import subtitles.subtitles
import utils.language_utils
import time


whisper_models = {}

def generate_subtitles(media, language, model="tiny"):
    if model not in whisper_models:
        m = whisper.load_model(model, download_root="models")
        whisper_models[model] = m
    model = whisper_models[model]
    subtiles_name = media.replace(".wav", ".srt").replace(".mp3", ".srt").replace(".mp4", ".srt").replace(".mkv",
                                                                                                          ".srt")
    t1 = time.time()
    res = model.transcribe(media, verbose=True, language=language, temperature=0.0, condition_on_previous_text=False)
    t2 = time.time()
    print("Transcription time: " + str(t2 - t1))
    s = subtitles.subtitles.Subtitles()
    for i in range(len(res["segments"])):
        start = int(res["segments"][i]["start"] * 1000)
        end = int(res["segments"][i]["end"] * 1000)
        text = res["segments"][i]["text"]
        if language == "sr" or language == "hr":
            text = utils.language_utils.serbocroatian_to_cyrillic(text)
        line = {"from": start, "to": end, "text": text}
        s.data.append(line)
    s.save(subtiles_name)
    return s
import whisper
import subtitles.subtitles
import utils.language_utils
import time


whisper_models = {}

DEFAULT_MODEL = "large"

def generate_subtitles(media, language, model=DEFAULT_MODEL, task="trabscribe"):
    if model not in whisper_models:
        m = whisper.load_model(model, download_root="models")
        whisper_models[model] = m
    model = whisper_models[model]
    subtiles_name = media.replace(".wav", ".srt").replace(".mp3", ".srt").replace(".mp4", ".srt").replace(".mkv",
                                                                                                          ".srt")
    t1 = time.time()
    res = model.transcribe(media, verbose=True, language=language, task=task, temperature=0.0, condition_on_previous_text=False)
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
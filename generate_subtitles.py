import whisper
import subtitles.subtitles
import utils.language_utils

def generate_subtitles(media, language, model="large"):
    model = whisper.load_model(model, download_root="models")
    res = model.transcribe(media, verbose=True, language=language, temperature=0.0)
    s = subtitles.subtitles.Subtitles()
    for i in range(len(res["segments"])):
        start = int(res["segments"][i]["start"] * 1000)
        end = int(res["segments"][i]["end"] * 1000)
        text = res["segments"][i]["text"]
        if language == "sr" or language == "hr":
            text = utils.language_utils.serbocroatian_to_cyrillic(text)
        line = {"from": start, "to": end, "text": text}
        s.data.append(line)
    subtiles_name = media.replace(".wav", ".srt").replace(".mp3", ".srt").replace(".mp4", ".srt")
    s.save(subtiles_name)
    return

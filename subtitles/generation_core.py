import whisper
import subtitles.subs
import time
import numpy as np
import matplotlib.pyplot as plt
import subtitles.vad
import subtitles.textual_anomalies
import subprocess

whisper_models = {}
DEFAULT_MODEL = "large"


def generate(wav, sample_rate, language, vad, model=DEFAULT_MODEL, task="transcribe", t=None, prompt=None, level=0):
    t_start = 0
    t_end = 1000000000
    if t is not None:
        media = whisper.load_audio(wav, sr=sample_rate)
        media = media[t[0] * sample_rate // 1000: t[1] * sample_rate // 1000]
        t_start = t[0]
        t_end = t[1]
    else:
        media = wav
    if model not in whisper_models:
        m = whisper.load_model(model, download_root="models")
        whisper_models[model] = m
    the_model = whisper_models[model]
    if prompt is None:
        res = the_model.transcribe(media, verbose=True, language=language, task=task, temperature=0.0,
                                   condition_on_previous_text=False)
    else:
        res = the_model.transcribe(media, verbose=True, language=language, task=task, temperature=0.0,
                                   condition_on_previous_text=False, prompt=prompt)
    s = subtitles.subs.Subtitles()

    for i in range(len(res["segments"])):
        start = int(res["segments"][i]["start"] * 1000) + t_start
        end = min(int(res["segments"][i]["end"] * 1000) + t_start, t_end)
        the_text = res["segments"][i]["text"]
        line = {"from": start, "to": end, "text": the_text, "logprob": res["segments"][i]["avg_logprob"]}

        # print(the_text, res["segments"][i]["avg_logprob"])

        # strict_intervals = vad.get_intervals(0.9, t=(start, end))
        """
        if level == 0:
            generated_subs = generate(wav, sample_rate, language, vad, model='large', task=task,
                                      t=(start, end), prompt="", level=1)
            content = generated_subs.get_content()
            phonetic_similarity = subtitles.textual_anomalies.phonetic_similarity(the_text, content)
            print(phonetic_similarity, the_text, content)
        """

        text_anomalous = subtitles.textual_anomalies.is_anomalous(the_text)
        if text_anomalous:
            if level == 0:
                strict_intervals = vad.get_intervals(0.9, t=(start, end))
                for j in range(len(strict_intervals)):
                    generated_subs = generate(wav, sample_rate, language, vad, model=model, task=task,
                                              t=strict_intervals[j], prompt="", level=1)

                    if len(generated_subs.data) == 0:
                        interval_length = strict_intervals[j][1] - strict_intervals[j][0]
                        for q in range(5):
                            interval_start = round(strict_intervals[j][0] + q * interval_length / 10)
                            generated_subs = generate(wav, sample_rate, language, vad, model=model, task=task,
                                                      t=(interval_start, strict_intervals[j][1]), prompt="", level=1)
                            if len(generated_subs.data) > 0:
                                break
                    s.data.extend(generated_subs.data)
        else:
            s.data.append(line)
    return s


def generate_subtitles(media, language, model=DEFAULT_MODEL, task="transcribe"):
    wav_file = media.replace("mp4", "wav")
    subprocess.run(["ffmpeg", "-i", media, "-y", wav_file])
    sample_rate = 16000

    vad = subtitles.vad.VAD(wav_file)
    vad.plot()

    intervals = vad.get_intervals()
    if vad.is_music():
        intervals = vad.get_intervals_for_music()

    subtitle_list = []
    for i in range(len(intervals)):
        newsub = generate(wav_file, sample_rate, language, vad, model=model, task=task, t=intervals[i], prompt="",
                          level=0)
        subtitle_list.append(newsub)
    merged = subtitles.subs.Subtitles.merge_subtitles(subtitle_list)
    subtiles_name = media.replace(".wav", ".srt").replace(".mp3", ".srt").replace(".mp4", ".srt").replace(".mkv",
                                                                                                          ".srt")
    merged.save(subtiles_name)
    return merged


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
    file = "data//youtube//_media.mp4"
    detected_lang = detect_language("data//youtube//_media.mp4")
    s = generate_subtitles("data//youtube//_media.mp4", detected_lang)
    # s = generate_subtitles("data//youtube//___media.mp4", 'en', t=(10*60+25, 11*60+20))
    # s = generate_subtitles("data//content//Serbian//Cartoons//Urfin Jus//Urfin Jus.mp4", 'hr')
    # s = generate_subtitles("data//content//Russian//Music//Frozen, Let it go//video.mp4", 'hr')

    s.save("data//temp.srt")

    text = ""
    for i in range(len(s.data)):
        text += s.data[i]["text"]
    print(text)

from pytube import YouTube
import time
import xml.etree.ElementTree as ET
from youtube_transcript_api import YouTubeTranscriptApi
import subtitles.subs


def download(link, audio=True):
    obj = YouTube("https://www.youtube.com/watch?v=" + link)
    obj = obj.streams.filter(only_audio=audio, subtype="mp4").first()
    t1 = time.time()
    obj.download(output_path="data//youtube//", filename="_media." + obj.subtype)
    t2 = time.time()
    print("Downloaded in " + str(t2 - t1) + " seconds")


def xml_to_subs(xml_data):
    root = ET.fromstring(xml_data)
    for body in root:
        for child in body:
            print(child.attrib["t"], child.attrib["d"], child.text)


def transcript_to_subs(transcript):
    res = subtitles.subs.Subtitles()
    for i in range(len(transcript)):
        text = transcript[i]["text"]
        text = text.replace(u'\xa0', u' ')
        if "\n" in text:
            if len(text.split("\n")) == 2:
                first_line = text.split("\n")[0]
                second_line = text.split("\n")[1]
                if len(second_line) > 0 and second_line[0].isupper() and len(first_line) > 0 and first_line[
                    -1].isalpha():
                    text = first_line + " " + second_line
                else:
                    if len(first_line) > 0 and first_line[-1] == ' ':
                        text = first_line + second_line
                    else:
                        text = first_line + " " + second_line
            else:
                text = text.replace("\n", "")
        res.data.append(
            {
                "from": int(transcript[i]["start"] * 1000),
                "to": int(transcript[i]["start"] * 1000 + transcript[i]["duration"] * 1000),
                "text": text
            })
    return res


def get_rank(code):
    ranks = {
        'en': 0,
        'de': 3,
        'fr': 2,
        'es': 1,
        'it': 4,
        'pt': 5,
        'ru': 6,
        'ja': 7,
    }
    if code in ranks:
        return ranks[code]
    return 100


def pull_subs(link, language, only_manual=False):
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(link)
    except:
        return None

    detected_language = None

    translatable_transcripts = []

    for transcript in transcript_list:
        if not transcript.is_generated and language in transcript.language_code:
            t = transcript.fetch()
            res = transcript_to_subs(t)
            return res

        if transcript.is_generated:
            detected_language = transcript.language_code

        if not only_manual:
            if not transcript.is_generated and transcript.is_translatable and language != "og":
                translatable_transcripts.append(transcript)

    if not only_manual:
        translatable_transcripts.sort(key=lambda x: get_rank(x.language_code))
        if len(translatable_transcripts) > 0:
            translation = translatable_transcripts[0].translate(language)
            t = translation.fetch()
            res = transcript_to_subs(t)
            return res

    if detected_language is not None and language == 'og':
        for transcript in transcript_list:
            if not transcript.is_generated and detected_language in transcript.language_code:
                t = transcript.fetch()
                res = transcript_to_subs(t)
                return res
    return None

    """
    obj = YouTube("https://www.youtube.com/watch?v=" + link)
    captions = obj.captions.lang_code_index
    keys = captions.keys().to_list()

    found_language = None
    for i in range(len(keys)):
        if language in keys[i]:
            language = keys[i]
            break
    if language in captions:
        caption = captions[language]
        xml = caption.xml_captions
        res = xml_to_subs(xml)
    else:
        return None
    """


if __name__ == "__main__":
    # download("https://www.youtube.com/watch?v=gcKh4WvoSBs", False)
    subs = pull_subs("q4DF3j4saCE", "en")
    print(subs.get_content())

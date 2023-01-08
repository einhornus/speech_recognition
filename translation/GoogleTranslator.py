# import Translator
from typing import Optional, List
import six
from google.cloud import translate_v2 as translate
import time

from src.translation.Translator import Translator as Base


class GoogleTranslator(Base):
    def __init__(self):
        super().__init__()
        self.name = 'Google'

    def do_translate(self, data: List[str], src: Optional[str], dest: Optional[str]):
        if src == 'kr' and dest == 'en':
            src = 'ka'
            dest = 'ru'

        client = translate.Client.from_service_account_json("..//access_tokens//Google.json")
        result = client.translate(data, source_language=src, target_language=dest,
                                  format_="html")
        res = []
        for i in range(len(result)):
            translation_result = result[i]["translatedText"]
            translation_result = translation_result.replace("&#39;", "'")
            translation_result = translation_result.replace("&quot;", "\"")
            res.append(translation_result)
        return res

from abc import ABC
from translation.Translator import Translator as Base
from typing import Optional
from urllib import request, parse
import json
from transformers import MBartForConditionalGeneration, MBart50TokenizerFast
from nltk.tokenize import sent_tokenize
from transformers import pipeline
import dl_translate as dlt
import os

class MultiTranslator(Base):
    def get_code(self, lang):
        for i in range(len(self.codes)):
            if lang+"_"in self.codes[i]:
                return self.codes[i]

    def __init__(self):
        super().__init__()
        self.model = None
        self.name = "m2m100"

        self.codes = [
            "ar_AR",
            "cs_CZ",
            "de_DE",
            "en_XX",
            "es_XX",
            "et_EE",
            "fi_FI",
            "fr_XX",
            "gu_IN",
            "hi_IN",
            "it_IT",
            "ja_XX",
            "kk_KZ",
            "ko_KR",
            "lt_LT",
            "lv_LV",
            "my_MM",
            "ne_NP",
            "nl_XX",
            "ro_RO",
            "ru_RU",
            "si_LK",
            "tr_TR",
            "vi_VN",
            "zh_CN",
            "af_ZA",
            "az_AZ",
            "be_IN",
            "fa_IR",
            "he_IL",
            "hr_HR",
            "id_ID",
            "ka_GE",
            "km_KH",
            "mk_MK",
            "ml_IN",
            "mn_MN",
            "mr_IN",
            "pl_PL",
            "ps_AF",
            "pt_XX",
            "sv_SE",
            "sw_KE",
            "ta_IN",
            "te_IN",
            "th_TH",
            "tl_XX",
            "uk_UA",
            "ur_PK",
            "xh_ZA",
            "gl_ES",
            "sl_SI"
        ]

    def load_model(self, a, b):
        self.model = MBartForConditionalGeneration.from_pretrained("facebook/mbart-large-50-many-to-one-mmt", cache_dir="models//translation_model")
        self.tokenizer = MBart50TokenizerFast.from_pretrained("facebook/mbart-large-50-many-to-one-mmt", cache_dir="models//translation_tokenizer")
        #self.model = dlt.TranslationModel("models", model_family="mbart50")
        #self.model = dlt.TranslationModel(model_or_path="models//translation_model", tokenizer_path="models//translation_tokenizer", model_family="mbart50")
        #tokenizer = AutoTokenizer.from_pretrained("facebook/mbart-large-50-many-to-one-mmt", cahce_dir="models")

    def do_translate(self, text, src: Optional[str], dest: Optional[str]):
        self.tokenizer.src_lang = self.get_code(src)
        self.tokenizer.dst_lang = self.get_code(dest)

        res = []
        for t in range(len(text)):
            encoded_hi = self.tokenizer(text[t], padding=True, truncation=True, return_tensors="pt")
            generated_tokens = self.model.generate(**encoded_hi)
            res.append(self.tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0])
            print(res[-1])
        return res

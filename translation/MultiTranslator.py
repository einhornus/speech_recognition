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
    def __init__(self):
        super().__init__()
        self.model = None
        self.name = "m2m100"

    def load_model(self, a, b):
        self.model = MBartForConditionalGeneration.from_pretrained("facebook/mbart-large-50-many-to-one-mmt", cache_dir="models//translation_model")
        self.tokenizer = MBart50TokenizerFast.from_pretrained("facebook/mbart-large-50-many-to-one-mmt", cache_dir="models//translation_tokenizer")
        #self.model = dlt.TranslationModel("models", model_family="mbart50")
        #self.model = dlt.TranslationModel(model_or_path="models//translation_model", tokenizer_path="models//translation_tokenizer", model_family="mbart50")
        #tokenizer = AutoTokenizer.from_pretrained("facebook/mbart-large-50-many-to-one-mmt", cahce_dir="models")

    def do_translate(self, text, src: Optional[str], dest: Optional[str]):
        self.tokenizer.src_lang = "en_XX"
        self.tokenizer.dst_lang = "ru_RU"

        encoded_hi = self.tokenizer(text, padding=True, truncation=True, return_tensors="pt")
        generated_tokens = self.model.generate(**encoded_hi)
        res = self.tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)

        #res = self.model.translate(text, source=src, target=dest)
        print(res)
        return res

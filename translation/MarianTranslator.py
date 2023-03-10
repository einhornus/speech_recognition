from abc import ABC
from translation.Translator import Translator as Base
from typing import Optional
from urllib import request, parse
import json
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from nltk.tokenize import sent_tokenize
from transformers import pipeline
from transformers import MarianMTModel, MarianTokenizer

"""
class MariamTranslator(Base):

    def __init__(self):
        super().__init__()
        self.models = {}
        self.tokenizers = {}
        self.name = 'Mariam'

    def do_translate(self, text, src: Optional[str], dest: Optional[str]):
        if src == 'pt' and dest == 'en':
            return self.translate(self.do_translate(text, 'pt', 'ca'), 'ca', 'en')

        model_name = src + "-" + dest
        print("Mariam downloading", model_name)
        if not model_name in self.models:
            tokenizer = AutoTokenizer.from_pretrained("Helsinki-NLP/opus-mt-"+model_name)
            model = AutoModelForSeq2SeqLM.from_pretrained("Helsinki-NLP/opus-mt-"+model_name)
            self.models[model_name] = model
            self.tokenizers[model_name] = tokenizer
            model.eval()
        model = self.models[model_name]
        tokenizer = self.tokenizers[model_name]
        translated = model.generate(**tokenizer(text, return_tensors="pt", padding=True), temperature=0.6)
        res = [tokenizer.decode(t, skip_special_tokens=True) for t in translated]
        return res

"""


def choose_model(src, dest):
    model_name = src + "-" + dest
    if src in ["ru", "uk", "be"] and dest == "en":
        model_name = "tc-big-zle-en"
    if src == "en" and dest in ["ru", "uk", "be"]:
        model_name = "tc-big-en-zle"
    if src == "hr" and dest == "en":
        model_name = "tc-big-sh-en"
    if src == "en" and dest in ["nl", "de", "af"]:
        model_name = "tc-big-gmw-gmw"
    if src == "en" and dest in ["sv", "da", "no"]:
        model_name = "tc-big-en-gmq"
    if src == "en" and dest == "es":
        model_name = "tc-big-en-es"
    if src == "en" and dest == "fr":
        model_name = "tc-big-en-fr"
    if src == "en" and dest == "it":
        model_name = "tc-big-en-it"
    if src == "en" and dest == "pt":
        model_name = "tc-big-en-pt"
    if src == "en" and dest == "ar":
        model_name = "tc-big-en-ar"
    if src == "en" and dest == "tr":
        model_name = "tc-big-en-tr"
    return model_name


class MarianTranslator(Base):
    available_models = [
        ["en", "es"],
        ["en", "de"],
        ["en", "fr"],
        ["en", "it"],
        ["en", "pt"],
        ["en", "ru"],
        ["en", "ja"],
        ["en", "ar"],
        ["en", "zh"],
        ["en", "nl"],
        ["en", "sv"],
        ["en", "da"],
        ["en", "no"],
        ["en", "ko"],
        ["en", "tr"],
        ["en", "ar"],
        ["en", "pl"],
        ["en", "cs"],
        ["ru", "en"],
        ["de", "en"],
        ["es", "en"],
        ["fr", "en"],
        ["it", "en"],
        ["nl", "en"],
        ["ja", "en"],
        ["zh", "en"],
        ["sv", "en"],
        ["da", "en"],
        ["no", "en"],
        ["ko", "en"],
        ["tr", "en"],
        ["ar", "en"],
        ["pl", "en"],
        ["cs", "en"]
    ]

    def __init__(self, models=None):
        super().__init__()
        self.models = {}
        self.tokenizers = {}
        self.name = "BigMarian"
        if not (models is None):
            for i in range(len(models)):
                self.load_model(models[i][0], models[i][1])

    def load_model(self, src, dest):
        found_pair = False
        for i in range(len(self.available_models)):
            if self.available_models[i][0] == src and self.available_models[i][1] == dest:
                found_pair = True
                break

        if not found_pair:
            return False

        if src != dest:
            model_name = choose_model(src, dest)
            if not model_name in self.models:
                print("Mariam downloading", model_name)
                try:
                    tokenizer = MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-" + model_name,
                                                                cache_dir="models//Marian")
                    model = MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-" + model_name,
                                                          cache_dir="models//Marian")
                except:
                    print("Mariam downloading failed", model_name)
                    return False
                self.models[model_name] = model
                self.tokenizers[model_name] = tokenizer
                model.eval()
        return True

    def do_translate(self, text, src, dest):
        choosen_model = choose_model(src, dest)
        self.load_model(src, dest)

        res = []
        for i in range(len(text)):
            if choosen_model in ['tc-big-en-zle', 'tc-big-gmw-gmw']:
                if dest == "ru":
                    new_sentences = [">>rus<< " + text[i]]
                if dest == "uk":
                    new_sentences = [">>ukr<< " + text[i]]
                if dest == "be":
                    new_sentences = [">>bel<< " + text[i]]
                if dest == "nl":
                    new_sentences = [">>nld<< " + text[i]]
                if dest == "de":
                    new_sentences = [">>deu<< " + text[i]]
                if dest == "af":
                    new_sentences = [">>afr<< " + text[i]]
                if dest == "sv":
                    new_sentences = [">>swe<< " + text[i]]
                if dest == "da":
                    new_sentences = [">>dan<< " + text[i]]
                if dest == "no":
                    new_sentences = [">>nob<< " + text[i]]
                if dest == "ar":
                    new_sentences = [">>ara<< " + text[i]]

            else:
                new_sentences = [text[i]]
            model = self.models[choosen_model]
            tokenizer = self.tokenizers[choosen_model]
            tokenized = tokenizer(new_sentences, return_tensors="pt", padding=True, truncation=True)
            translated = model.generate(**tokenized)
            sentences_translated = [tokenizer.decode(t, skip_special_tokens=True) for t in translated]

            for q in range(len(sentences_translated)):
                if sentences_translated[q] == "I don't know.":
                    sentences_translated[q] = '. '

            res_element = " ".join(sentences_translated)
            res.append(res_element)

        return res

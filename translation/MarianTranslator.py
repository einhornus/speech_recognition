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
    return model_name

class MarianTranslator(Base):
    def __init__(self, models=None):
        super().__init__()
        self.models = {}
        self.tokenizers = {}
        self.name = "BigMarian"
        if not (models is None):
            for i in range(len(models)):
                self.load_model(models[i][0], models[i][1])

    def load_model(self, src, dest):
        if src != dest:
            model_name = choose_model(src, dest)
            if not model_name in self.models:
                print("Mariam downloading", model_name)
                tokenizer = MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-" + model_name, cache_dir = "models//Marian")
                model = MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-" + model_name, cache_dir = "models//Marian")
                self.models[model_name] = model
                self.tokenizers[model_name] = tokenizer
                model.eval()

    def do_translate(self, text, src, dest):
        choosen_model = choose_model(src, dest)
        self.load_model(src, dest)

        res = []
        for i in range(len(text)):
            if choosen_model == 'tc-big-en-zle':
                if dest == "ru":
                    new_sentences = [">>rus<< "+text[i]]
                if dest == "uk":
                    new_sentences = [">>ukr<< "+text[i]]
                if dest == "be":
                    new_sentences = [">>bel<< "+text[i]]
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


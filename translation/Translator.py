from abc import abstractmethod
from typing import Optional, List
import hashlib
import sqlite3
import time
from threading import Thread
import os


class Translator():
    MAX_GROUP_SIZE = 4000

    def __init__(self):
        self.name = "UNKNOWN"

    @staticmethod
    def split(data, max_size):
        chunks = []
        group = []

        last_group_size = 0
        for i in range(len(data)):
            group.append(data[i])
            last_group_size += len(data[i][0])

            if i < len(data) - 1:
                if last_group_size + len(data[i + 1][0]) > max_size:
                    chunks.append(group)
                    last_group_size = 0
                    group = []
        if len(group) > 0:
            chunks.append(group)
        return chunks

    def calculate_latency(self, sentences, lang):
        t1 = time.time()
        r = self.do_translate(sentences, lang, 'en')
        t2 = time.time()
        return t2 - t1

    def translate(self, data, src: Optional[str], dest: Optional[str], db_path="data//translations.db"):
        if src == dest:
            return data

        is_list = isinstance(data, list)
        if not is_list:
            data = [data]

        if db_path is None:
            pairs = []
            for i in range(len(data)):
                pairs.append([data[i], i])

            res = []
            splitted_groups_pairs = Translator.split(pairs, self.MAX_GROUP_SIZE)
            for i in range(len(splitted_groups_pairs)):
                group = []
                for j in range(len(splitted_groups_pairs[i])):
                    group.append(splitted_groups_pairs[i][j][0])
                local_res = self.do_translate(group, src, dest)
                res.extend(local_res)
                print(local_res)
            return res

        results_array = []

        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        to_ask_phrases = []
        to_ask_indexes = []

        for i in range(len(data)):
            text = data[i]

            hash = hashlib.md5((text + src + dest + self.name).encode("utf8")).hexdigest()


            c.execute("SELECT text, src, dest, hash, translation, model FROM translations WHERE hash = ? AND model = ?",
                      (hash, self.name))
            records = c.fetchall()

            to_return = None

            if len(records) == 0:
                to_ask_phrases.append(text)
                to_ask_indexes.append(i)
            else:
                for i in range(len(records)):
                    if records[i][0] == text and records[i][1] == src and records[i][2] == dest and records[0][
                        5] == self.name:
                        print("Found ", (hash, src, dest, text, records[0][4]))
                        to_return = records[0][4]

            results_array.append(to_return)

        conn.commit()
        conn.close()

        if len(to_ask_phrases) > 0:
            pairs = []
            for i in range(len(to_ask_phrases)):
                pairs.append([to_ask_phrases[i], to_ask_indexes[i]])
            splitted_groups_pairs = Translator.split(pairs, self.MAX_GROUP_SIZE)

            questions_array = [[] for i in range(len(splitted_groups_pairs))]
            indexes_array = [[] for i in range(len(splitted_groups_pairs))]

            for i in range(len(splitted_groups_pairs)):
                for j in range(len(splitted_groups_pairs[i])):
                    questions_array[i].append(splitted_groups_pairs[i][j][0])
                    indexes_array[i].append(splitted_groups_pairs[i][j][1])

            for i in range(len(splitted_groups_pairs)):
                while True:
                    try:
                        res = self.do_translate(questions_array[i], src, dest)
                        conn = sqlite3.connect(db_path)
                        c = conn.cursor()

                        for j in range(len(res)):
                            ind = indexes_array[i][j]
                            question = questions_array[i][j]
                            answer = res[j]
                            results_array[ind] = answer
                            hash = hashlib.md5((question + src + dest + self.name).encode("utf8")).hexdigest()
                            c.execute(
                                "INSERT INTO translations (hash, src, dest, text, translation, model) VALUES (?, ?, ?, ?, ?, ?)",
                                (hash, src, dest, question, answer, self.name))
                            print("Added ", (hash, src, dest, question, answer))

                        conn.commit()
                        conn.close()

                        break
                    except Exception as e:
                        print('no success', e, 'in', self.name)
                        time.sleep(61)

        if not is_list:
            return results_array[0]
        else:
            return results_array

    @abstractmethod
    def do_translate(self, texts: List[str], src: Optional[str], dest: Optional[str]):
        pass

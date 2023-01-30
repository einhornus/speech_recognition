import json
import random
import sqlite3
import storage.bert
from sklearn.neighbors import KDTree
import translation.language_detection

TITLE_WEIGHT = 0.5
MAX_RESULTS = 6


class Catalogue:
    def __init__(self):
        conn = sqlite3.connect("data//database.db")
        c = conn.cursor()
        c.execute(
            "SELECT video_id, title, keywords, embedding, original_language, translation_language, thumbnail FROM videos")
        self.videos = []
        for row in c.fetchall():
            id = row[0]
            title = row[1]
            keywords = row[2]
            embedding = json.loads(row[3])
            original_language = row[4]
            translation_language = row[5]
            thumbnail = row[6]
            video = {
                "id": id,
                "keywords": keywords,
                "embedding": embedding,
                "title": title,
                "original_language": original_language,
                "translation_language": translation_language,
                "thumbnail": thumbnail,
            }
            self.videos.append(video)
        conn.commit()
        conn.close()
        print()

    def search(self, query, original_language="an", language="og"):
        candidates = []
        for video in self.videos:
            is_candidate = False
            if video["original_language"] == original_language or original_language == "an":
                if language == "og":
                    is_candidate = True
                if language != "og" and video["translation_language"] == language:
                    is_candidate = True
                if language != "og" and "og_"+video["translation_language"] == language:
                    is_candidate = True
            if is_candidate:
                candidates.append(video)
        random.shuffle(candidates)

        bert_query = None
        if query != "":
            bert_query = storage.bert.encode_bert(query)
        res = []
        for video in candidates:
            if bert_query is None:
                relevance = 0
            else:
                relevance = storage.bert.sim(bert_query, video["embedding"])
            res.append((video, relevance))

        res.sort(key=lambda x: x[1], reverse=True)

        result = []
        for i in range(len(res)):
            obj = {}
            obj["id"] = res[i][0]["id"]
            obj["language"] = language
            obj["original_language"] = original_language
            obj["title"] = res[i][0]["title"]
            obj["thumbnail"] = res[i][0]["thumbnail"]
            result.append(obj)

        if len(result) > MAX_RESULTS:
            result = result[:MAX_RESULTS]

        return result

    def add_video(self, video_id, title, content, keywords, thumbnail, duration, original_language,
                  translation_language, is_featured):
        conn = sqlite3.connect("data//database.db")
        content_embedding = storage.bert.encode_bert(content)[0]
        english_title = translation.language_detection.to_english(title)
        title_embedding = storage.bert.encode_bert(english_title)[0]

        CONTENT_WEIGHT = 1 - TITLE_WEIGHT
        embedding = []
        for i in range(len(title_embedding)):
            embedding.append(TITLE_WEIGHT * title_embedding[i] + CONTENT_WEIGHT * content_embedding[i])

        norm = 0
        for i in range(len(embedding)):
            norm += embedding[i] * embedding[i]
        norm = norm ** 0.5
        for i in range(len(embedding)):
            embedding[i] /= norm
        embedding_text = json.dumps(embedding)

        keywords_text = "; ".join(keywords)
        keywords_text = translation.language_detection.to_english(keywords_text)
        c = conn.cursor()
        c.execute("INSERT INTO videos VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                  (None, video_id, title, keywords_text, duration, thumbnail,
                   original_language, translation_language, 1 if is_featured else 0, embedding_text))
        conn.commit()
        conn.close()

        obj = {
            "id": video_id,
            "keywords": keywords,
            "embedding": embedding,
            "title": title,
            "original_language": original_language,
            "translation_language": translation_language,
        }
        self.videos.append(obj)

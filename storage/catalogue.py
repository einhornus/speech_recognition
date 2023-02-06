import json
import math
import random
import sqlite3
import storage.bert
from sklearn.neighbors import KDTree

import subtitles.subs
import translation.language_detection

TITLE_WEIGHT = 0.5
MAX_RESULTS = 12


class Catalogue:
    def __init__(self):
        conn = sqlite3.connect("data//database.db")
        c = conn.cursor()
        c.execute(
            "SELECT video_id, title, keywords, embedding, original_language, thumbnail, duration FROM videos")
        self.videos = []
        for row in c.fetchall():
            id = row[0]
            title = row[1]
            keywords = row[2]
            embedding = json.loads(row[3])
            original_language = row[4]
            thumbnail = row[5]
            duration = row[6]
            video = {
                "id": id,
                "keywords": keywords,
                "embedding": embedding,
                "title": title,
                "original_language": original_language,
                "thumbnail": thumbnail,
                "duration": duration,
                "languages": []
            }

            c.execute(
                "SELECT language FROM subtitles where video_id = ?", (id,))

            rows = c.fetchall()
            for row in rows:
                video["languages"].append(row[0])

            self.videos.append(video)
        conn.commit()
        conn.close()
        print()

    def search(self, query, original_language="an", language="og", number_of_results=MAX_RESULTS):
        """
        search - perform a search of videos based on query, original language and language

        This function searches through a list of videos (self.videos) and returns a list of videos that match the search criteria.
        The search criteria are defined by the input query string (query), original language (original_language) and the desired language (language).

        The function uses the "original_language" and "translation_language" fields of each video to determine if it is a candidate for the search.
        If a query string is provided, the function will encode the query with BERT and compute its similarity with the video embeddings to determine relevance.
        The function then sorts the results by relevance and returns the top results limited by the MAX_RESULTS constant.

        Inputs:
        query (str): The query string for the search.
        original_language (str, optional): The original language of the video. Defaults to "an".
        language (str, optional): The desired language of the video. Defaults to "og".

        Returns:
        list: A list of dictionaries representing the top matching videos, each containing the following fields:
        "id": the video id
        "language": the desired language of the video
        "original_language": the original language of the video
        "title": the title of the video
        "thumbnail": the thumbnail image of the video
        """

        query_words = query.split(" ")

        candidates = []
        for video in self.videos:
            video["similarity"] = 0
            is_candidate = False
            if video["original_language"] == original_language or original_language == "an":
                if language == "og":
                    is_candidate = True
                if language == "en" and video["original_language"] != "en":
                    is_candidate = True
                if language == "og_en" and video["original_language"] != "en":
                    is_candidate = True
                if language in video["languages"] and language != video["original_language"]:
                    is_candidate = True
                if len(language) == 5:
                    if language[3:] in video["languages"] and video["original_language"] != language[3:]:
                        is_candidate = True
                if is_candidate and video["id"]:
                    candidates.append(video)

        # random.shuffle(candidates)
        candidates.reverse()

        bert_query = None
        if query != "":
            bert_query = storage.bert.encode_bert(query)
        res = []
        for video in candidates:
            if bert_query is None:
                relevance = 0
            else:
                relevance = storage.bert.sim(bert_query, video["embedding"])
            keywords = video["keywords"].split("; ")
            matches_keywords = False
            for keyword in keywords:
                if keyword in query_words:
                    matches_keywords = True
            if matches_keywords:
                if relevance > 0:
                    relevance *= 2
            relevance += math.log(video["duration"]) * 0.03
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

        if len(result) > number_of_results:
            result = result[:number_of_results]

        return result

    @staticmethod
    def get_subtitles(video_id, language):
        """
        get_subtitles - get the subtitles for a video

        This function gets the subtitles for a video in a given language.

        Inputs:
        video_id (str): The id of the video.
        language (str): The language of the subtitles.

        Returns:
        str: The subtitles for the video in the given language or None if no subtitles are found.
        """

        if language == "og":
            conn = sqlite3.connect("data//database.db")
            c = conn.cursor()
            c.execute("SELECT original_language FROM videos WHERE video_id=?", (video_id,))
            language = None
            for row in c.fetchall():
                language = row[0]
            conn.commit()
            conn.close()

        print("Looking for subs for video " + video_id + " in language ", language)

        if language is None:
            return None

        conn = sqlite3.connect("data//database.db")
        c = conn.cursor()
        c.execute("SELECT content FROM subtitles WHERE video_id=? AND language=?", (video_id, language))
        content = None
        fetched = c.fetchall()
        if len(fetched) == 0:
            pass
        else:
            if len(fetched) > 1:
                raise Exception("More than one subtitle found for video " + video_id + " in language " + language)
            else:
                for row in fetched:
                    content = row[0]
        conn.commit()
        conn.close()
        if content is not None:
            print("Found subtitles for video " + video_id + " in language " + language + "!")
            return subtitles.subs.Subtitles(content=content)
        else:
            print("No subtitles for video " + video_id + " in language " + language + "!")
            return None

    @staticmethod
    def write_subtitles(video_id, language, content):
        """
        write_subtitles - write the subtitles for a video

        This function writes the subtitles for a video in a given language.

        Inputs:
        video_id (str): The id of the video.
        language (str): The language of the subtitles.
        content (str): The content of the subtitles.
        """
        conn = sqlite3.connect("data//database.db")
        c = conn.cursor()
        c.execute("SELECT content FROM subtitles WHERE video_id=? AND language=?", (video_id, language))
        if len(c.fetchall()) == 0:
            c.execute("INSERT INTO subtitles VALUES (?, ?, ?, ?)", (None, video_id, language, content))
        else:
            c.execute("UPDATE subtitles SET content=? WHERE video_id=? AND language=?", (content, video_id, language))
        conn.commit()
        conn.close()

    def update_languages(self, video_id):
        conn = sqlite3.connect("data//database.db")
        c = conn.cursor()
        languages = []
        c.execute(
            "SELECT language FROM subtitles where video_id = ?", (video_id,))
        rows = c.fetchall()
        for row in rows:
            languages.append(row[0])
        conn.commit()
        conn.close()
        for i in range(len(self.videos)):
            if self.videos[i]["id"] == video_id:
                self.videos[i]["languages"] = languages

    def add_video(self, video_id, title, content, keywords, thumbnail, duration, original_language, is_featured):

        """
            This function is used to add video information to the database and an in-memory list of videos.

            The function starts by connecting to an SQLite database file, "data//database.db". It then uses the BERT
            encoder from the "storage" module to generate an embedding for the content and the title of the video, in
            English. The two embeddings are combined using a weighting factor, `TITLE_WEIGHT`, to produce a single
            video embedding, which is then normalised to have a Euclidean norm of 1.

            The list of keywords is joined into a single string, with each keyword separated by a semicolon, and
            translated into English using the language detection module. The video information is then inserted into the
            "videos" table in the SQLite database using an SQL INSERT statement.

            Finally, a dictionary containing the video information is appended to the "videos" list, which is an attribute
            of the class.

            Args:
            - video_id (str): A string representing the identifier of the video.
            - title (str): The title of the video, in its original language.
            - content (str): The full content of the video.
            - keywords (List[str]): A list of strings representing the keywords associated with the video.
            - thumbnail (str): A string representing the path to the thumbnail image of the video.
            - duration (int): The length of the video in seconds.
            - original_language (str): A string representing the original language of the video.
            - translation_language (str): A string representing the translation language of the video.
            - is_featured (bool): A Boolean value indicating whether the video is featured or not.

            Returns:
            None
        """

        print("Writing video to database...")

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
        c.execute("INSERT INTO videos VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                  (None, video_id, title, keywords_text, duration, thumbnail,
                   original_language, 1 if is_featured else 0, embedding_text))

        conn.commit()
        conn.close()

        obj = {
            "id": video_id,
            "keywords": keywords_text,
            "embedding": embedding,
            "title": title,
            "thumbnail": thumbnail,
            "duration": duration,
            "original_language": original_language,
            "languages": []
        }

        self.videos.append(obj)

    def is_video_exists(self, id):
        for video in self.videos:
            if video["id"] == id:
                return True
        return False

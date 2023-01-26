import storage.bert

DESCRIPTION_LIMIT = 512


class Video:
    def __init__(self, id, original_language, language, title, description, keywords, content, duration,
                 thumbnail):
        self.id = id
        self.original_language = original_language
        self.language = language
        self.title = title
        self.duration = duration
        if content is not None:
            self.content_embedding = storage.bert.encode_bert(content)
        self.keywords = keywords
        self.description = description
        if len(description) > DESCRIPTION_LIMIT:
            self.description = description[:DESCRIPTION_LIMIT]
        self.thumbnail = thumbnail

    def to_json(self):
        return {
            "id": self.id,
            "original_language": self.original_language,
            "language": self.language,
            "title": self.title,
            "description": self.description,
            "keywords": self.keywords,
            "content_embedding": self.content_embedding,
            "duration": self.duration,
            "thumbnail": self.thumbnail
        }

    @staticmethod
    def from_json(obj):
        res = Video(obj["id"], obj["original_language"], obj["language"], obj["title"], obj["description"],
                    obj["keywords"], None, obj["duration"], obj["thumbnail"])
        res.content_embedding = obj["content_embedding"]
        return res

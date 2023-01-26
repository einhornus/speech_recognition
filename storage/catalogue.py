import json
import storage.video

class Catalogue:
    def __init__(self):
        list = json.load(open("data//catalogue.json", "r", encoding="utf-8"))
        self.videos = []
        for i in range(len(list)):
            self.videos.append(storage.video.Video.from_json(list[i]))

    def save(self):
        list = []
        for i in range(len(self.videos)):
            list.append(self.videos[i].to_json())

        with open("data//catalogue.json", "w", encoding="utf-8") as f:
            json.dump(list, f, ensure_ascii=False, indent=4)

    def add_video(self, video):
        self.videos.append(video)
        self.save()
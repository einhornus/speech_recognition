import json
import scrapetube


def analyze():
    data = json.load(open("data//youtube_parsing//YouTubeDataset_withChannelElapsed.json", "r", encoding="utf-8"))
    for i in range(len(data)):
        data[i]["likes/views"] = float(data[i]["likes/views"])
    data.sort(key=lambda x: x["likes/views"], reverse=True)

    k = 0
    for i in range(len(data)):
        if data[i]["videoCategoryId"] == "37":
            print("https://www.youtube.com/watch?v="+data[i]["videoId"])
            k += 1
    print(k)

def search():
    videos = scrapetube.get_search("devojka", sort_by="rating")
    for video in videos:
        print(video['videoId'])

if __name__ == "__main__":
    search()
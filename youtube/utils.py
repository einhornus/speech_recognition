from pytube import YouTube
import json
import xml.etree.ElementTree as ElementTree
#import HTMLParser


def get_size(link):
    obj = YouTube("https://www.youtube.com/watch?v=" + link)
    obj = obj.streams.filter(only_audio=True).first()
    return obj.filesize

def get_id(link):
    return link.split("=")[1]

def get_attributes(obj):
    link = obj["link"]
    yt = YouTube("https://www.youtube.com/watch?v=" + link)
    obj["duration"] = yt.length
    obj["description"] = yt.description
    obj["title"] = yt.title
    obj["publish_date"] = yt.publish_date
    obj["thumbnail"] = yt.thumbnail_url
    obj["keywords"] = yt.keywords


if __name__ == "__main__":
    print(get_size("nE9UaU3eZDc"))

from pytube import YouTube

def get_size(link):
    obj = YouTube(link)
    obj = obj.streams.filter(only_audio=True).first()
    return obj.filesize


def get_id(link):
    return link.split("=")[1]
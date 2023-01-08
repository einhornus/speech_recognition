from pytube import YouTube



def get_size(link):
    obj = YouTube("https://www.youtube.com/watch?v="+link)
    obj = obj.streams.filter(only_audio=True).first()
    return obj.filesize


def get_id(link):
    return link.split("=")[1]

def get_duration(link):
    obj = YouTube("https://www.youtube.com/watch?v=" + link)
    return obj.length


if __name__ == "__main__":
    print(get_size("FoWkq8hggto"))
from pytube import YouTube
import time

def download(link):
    obj = YouTube(link)
    obj = obj.streams.filter(only_audio=True).first()
    t1 = time.time()
    obj.download(output_path="data//youtube//", filename="___media.mp4")
    t2 = time.time()
    print("Downloaded in " + str(t2 - t1) + " seconds")

#download("https://www.youtube.com/watch?v=S-Pcg8qR8-g")

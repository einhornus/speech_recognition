import time
import requests
import json
import scrapetube

#url = "http://128.199.46.26:8009/"
url = "http://127.0.0.1:8009/"


kurzgesagt_videos = [
    "q4DF3j4saCE",
    "Pj-h6MEgE7I",
    "KRvv0QdruMQ",
    "lheapd7bgLA",
    "VB_GWz25B3Q",
    "rhFK5_Nx9xY",
    "ck4RGeoHFko",
    "QImCld9YubE",
    "H6u0VBqNBQ8",
    "DHyUYg8X31c",
    "JQVmkDUkZT4",
    "sNhhvQGsMEc",
    "1fQkVqno-uI",
]

for i in range(len(kurzgesagt_videos)):
    res = requests.get(url + "subtitles", params={
        'id': kurzgesagt_videos[i],
        'language': 'og',
    })
    obj = json.loads(res.text)
    print(obj)

    res = requests.get(url + "subtitles", params={
        'id': kurzgesagt_videos[i],
        'language': 'og_ru',
    })
    obj = json.loads(res.text)
    print(obj)

    res = requests.get(url + "subtitles", params={
        'id': kurzgesagt_videos[i],
        'language': 'og_de',
    })
    obj = json.loads(res.text)
    print(obj)




kurzgesagt_videos = [
    "pb4YoMjcYM4",
    "w7daiJHfjoY",
    "m62QcCAkm88",
]

for i in range(len(kurzgesagt_videos)):
    res = requests.get(url + "subtitles", params={
        'id': kurzgesagt_videos[i],
        'language': 'og',
    })
    obj = json.loads(res.text)
    print(obj)

    res = requests.get(url + "subtitles", params={
        'id': kurzgesagt_videos[i],
        'language': 'og_ru',
    })
    obj = json.loads(res.text)
    print(obj)

    res = requests.get(url + "subtitles", params={
        'id': kurzgesagt_videos[i],
        'language': 'og_de',
    })
    obj = json.loads(res.text)
    print(obj)

    res = requests.get(url + "subtitles", params={
        'id': kurzgesagt_videos[i],
        'language': 'og_en',
    })
    obj = json.loads(res.text)
    print(obj)



res = requests.get(url + "subtitles", params={
    'id': "H_QimWv6t6I",  #кошачий передоз
    'language': 'og',
})
obj = json.loads(res.text)
print(obj)


res = requests.get(url + "subtitles", params={
    'id': "H_QimWv6t6I",  #кошачий передоз
    'language': 'og_en',
})
obj = json.loads(res.text)
print(obj)

res = requests.get(url + "subtitles", params={
    'id': "H_QimWv6t6I",  #кошачий передоз
    'language': 'og_de',
})
obj = json.loads(res.text)
print(obj)



res = requests.get(url + "subtitles", params={
    'id': "MyMT4DR8-PM",  #летучая мышца
    'language': 'og',
})
obj = json.loads(res.text)
print(obj)


res = requests.get(url + "subtitles", params={
    'id': "MyMT4DR8-PM",  #летучая мышца
    'language': 'og_en',
})
obj = json.loads(res.text)
print(obj)

res = requests.get(url + "subtitles", params={
    'id': "MyMT4DR8-PM",  #летучая мышца
    'language': 'og_nl',
})
obj = json.loads(res.text)
print(obj)

res = requests.get(url + "subtitles", params={
    'id': "MndCuzxl1kk", #clip
    'language': 'og',
})
obj = json.loads(res.text)
print(obj)

url = "http://127.0.0.1:8009/"
res = requests.get(url + "subtitles", params={
    'id': "MndCuzxl1kk", #clip
    'language': 'og_ru',
})
obj = json.loads(res.text)
print(obj)

res = requests.get(url + "subtitles", params={
    'id': "0cLWSa0ABBM", #нгема
    'language': 'og',
})
obj = json.loads(res.text)
print(obj)

res = requests.get(url + "subtitles", params={
    'id': "0cLWSa0ABBM", #нгема
    'language': 'og_en',
})
obj = json.loads(res.text)
print(obj)

res = requests.get(url + "subtitles", params={
    'id': "0cLWSa0ABBM", #нгема
    'language': 'og_ru',
})
obj = json.loads(res.text)
print(obj)
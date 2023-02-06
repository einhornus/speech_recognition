import time
import requests
import json
import scrapetube

# url = "http://128.199.46.26:8009/"
url = "http://127.0.0.1:8009/"

channels = [
    {
        "name": "kurzgesagt english",
        "videos": [
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
        ],
        "languages": ["og"]
    },
    {
        "name": "vsauce",
        "videos": [
            "jHbyQ_AQP8c",
            "_6nSOgsI_vo",
            "R3unPcJDbCc",
            "Z0zConOPZ8Y",
            "eiAx2kqmUpQ",
            "4e_kz79tjb8",
            "DAcjV60RnRw",
            "rYXdsOEWBj0",
            "L6S5amkCoyc",
            "MVpkeBYZOrE",
            "aHtjhCxRIa4",
            "IGK2KprU-To",
            "1T4XMNN4bNM",
            "E4HGfagANiQ",
            "e5jDspIC4hY",
            "rltpH6ck2Kc",
        ],
        "languages": ["og"]
    },
    {
        "name": "kurzgesagt german",
        "videos": [
            "pb4YoMjcYM4",
            "w7daiJHfjoY",
            "m62QcCAkm88",
        ],
        "languages": ["og"]
    },
    {
        "name": "redroom",
        "videos": [
            "_K9N0xWBbuM",
            "mASH4o5oa98",
            "Nft7eSj7j30",
            "fV2wQMHau98",
            "CbSPKi5hRI0",
            "esExWM4QUNo",
            "GDr3d8OiNPc",
        ],
        "languages": ["og"]
    },
]


def request_channels():
    for channel in channels:
        videos = channel["videos"]
        languages = channel["languages"]
        for i in range(len(videos)):
            for j in range(len(languages)):
                res = requests.get(url + "subtitles", params={
                    'id': videos[i],
                    'language': languages[j],
                })
                obj = json.loads(res.text)
                print(obj)


request_channels()
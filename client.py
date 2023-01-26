import time
import requests
import json

#url = "http://128.199.46.26:8009/"


url = "http://127.0.0.1:8009/"
# res = requests.get(url+"greet", params={'model':'nl', 'full_text':'ru'})
res = requests.get(url + "search", params={
    'query': "universe",
    'language': 'undefined',
    'original_language': 'undefined'
})
obj = json.loads(res.text)

for i in range(len(obj)):
    print(obj[i]["title"])
print(obj)
exit(0)

url = "http://127.0.0.1:8009/"
# res = requests.get(url+"greet", params={'model':'nl', 'full_text':'ru'})
res = requests.get(url + "subtitles", params={
    'id': "2i3u8VJjzBQ",
    'language': "og_fr"
})
obj = json.loads(res.text)
print(obj)
exit(0)

res = requests.get(url + "subtitles", params={
    'id': "uGVhmT07UUU",
    'language': "en"
})
obj = json.loads(res.text)
print(obj)

res = requests.get(url + "subtitles", params={
    'id': "uGVhmT07UUU",
    'language': "og_en"
})
obj = json.loads(res.text)
print(obj)

res = requests.get(url + "subtitles", params={
    'id': "uGVhmT07UUU",
    'language': "og_en_hints"
})
obj = json.loads(res.text)
print(obj)

"""
time.sleep(20)

res = requests.get(url + "request", params={
    'link': "ta0GhTt0iI8",
    'do_translate': True
})
obj = json.loads(res.text)
print(obj)

time.sleep(5)

res = requests.get(url + "request", params={
    'link': "9xgtuRqBS5A",
    'do_translate': True
})
obj = json.loads(res.text)
print(obj)
"""
# sudo certbot certonly --standalone --agree-tos --preferred-challenges http -d domain-name.com
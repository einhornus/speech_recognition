import time
import requests
import json

#url = "http://128.199.46.26:8009/"


url = "http://127.0.0.1:8009/"
# res = requests.get(url+"greet", params={'model':'nl', 'full_text':'ru'})
res = requests.get(url + "request", params={
    'link': "https://www.youtube.com/watch?v=uGVhmT07UUU",
    'do_translate': True
})
obj = json.loads(res.text)
print(obj)

time.sleep(20)

res = requests.get(url + "request", params={
    'link': "https://www.youtube.com/watch?v=ta0GhTt0iI8",
    'do_translate': True
})
obj = json.loads(res.text)
print(obj)

time.sleep(5)

res = requests.get(url + "request", params={
    'link': "https://www.youtube.com/watch?v=9xgtuRqBS5A",
    'do_translate': True
})
obj = json.loads(res.text)
print(obj)

# sudo certbot certonly --standalone --agree-tos --preferred-challenges http -d domain-name.com
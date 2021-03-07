import requests
from threading import Thread

def start():
    url = "http://localhost:15234/createArticle"

    payload = {
        'token': 'd1d1fe0473879f79d51a38d081cdeb8f220fa1412295fbf9c83832fda02b983f3365fd8ccec985cd8ca1c8ec47556a32003bb06cbb78f627c7d5dc8a6edf1fe2',
        'title': 'Котики захватили мир',
        'content': 'ОГО!',
        'source': 'source',
        'tags': '["Политика", "Что-то еще"]',
        'description': 'fdfd',
        'coverImage': 'https://avatars.mds.yandex.net/get-zen_doc/3769481/pub_5ef329359e2eda07265a9082_5ef34be07c87480b6789167d/scale_1200',
        'main': '1'}
    files = [

    ]
    headers = {}

    response = requests.request("POST", url, headers=headers, data=payload, files=files)

    print(response.text)


while (True):
    t1 = Thread(target=start, args=())
    t1.start()

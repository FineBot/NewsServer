import requests

while (True):
    url = "http://localhost:15234/createArticle"

    payload = {
        'token': 'aca072693df697fcd37f0a153914fb4fbf846ef12623d7c57a938d92b4c1660ece2292f4a8c77b593dcb70635e5cc29484deccd76a03e96612162defdc0b034f',
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
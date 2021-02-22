import json

def e404():
    return json.dumps({"error": {
        "code": 404,
        "text": "Method doesn't exist",
        "text_ru": "Метод не существует"
    }}, ensure_ascii=False)


def e500():
    return json.dumps({"error": {
        "code": 500,
        "text": "Server error",
        "text_ru": "Ошибка сервера"
    }}, ensure_ascii=False)

def eNotLoginOrPassword():
    return json.dumps({"error": {
        "code": 1,
        "text": "Wrong username or password",
        "text_ru": "Неправильный логин или пароль"
    }}, ensure_ascii=False)

def eNotPermissions():
    return json.dumps({"error": {
        "code": 2,
        "text": "No access",
        "text_ru": "Нет доступа"
    }}, ensure_ascii=False)

def eOnlyPost():
    return json.dumps({"error": {
        "code": 3,
        "text": "Only POST requests",
        "text_ru": "Только POST запросы"
    }}, ensure_ascii=False)

def eMissing(name):
    return json.dumps({"error": {
        "code": 4,
        "text": name+" is missing",
        "text_ru": name+" отсутствует",
        "name":name
    }}, ensure_ascii=False)
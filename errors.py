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
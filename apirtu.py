from flask import request
import json
import errors
import sqlite3 as sl
import hashlib
import time
import random

authorized=False
userId=-1
name=None

class apiClass:
    def __init__(self,method):
        if("token" in request.values):
            con = sl.connect('site.db')
            cur = con.cursor()
            obj = cur.execute("SELECT * FROM tokens WHERE token=(?)",(request.values['token'],)).fetchall()
            if(len(obj)==1):
                userId=obj[0][1]
                name=cur.execute("SELECT * FROM users WHERE id=(?)",(userId,)).fetchall()[0][1]
                authorized=True


        if(method=="getNews"):
            return apiClass.getNews(self)
        elif(method=="login"):
            return apiClass.createToken(self)
        else: return errors.e404()

    def getNews(self):
        con = sl.connect('site.db')
        cur=con.cursor()
        result = {"result":{"main":[],"all":[]}}

        obj = cur.execute("SELECT * FROM news WHERE main=1 ORDER BY publishedAt DESC LIMIT 0,100").fetchall()
        for i in range(0, len(obj)):
            result["result"]["main"].append({
                "id": obj[i][0],
                "title": obj[i][1],
                "content": obj[i][2],
                "source": obj[i][3],
                "tags": obj[i][4],
                "author": obj[i][5],
                "description": obj[i][6],
                "coverImage": obj[i][7],
                "publishedAt": obj[i][8],
            })

        obj=cur.execute("SELECT * FROM news WHERE main=0 ORDER BY publishedAt DESC LIMIT 0,100").fetchall()
        for i in range(0,len(obj)):
            result["result"]["all"].append({
                "id":obj[i][0],
                "title":obj[i][1],
                "content":obj[i][2],
                "source":obj[i][3],
                "tags":obj[i][4],
                "author":obj[i][5],
                "description":obj[i][6],
                "coverImage":obj[i][7],
                "publishedAt":obj[i][8],
            })
        return json.dumps(result,ensure_ascii=False)

    def createArticle(self):
        pass

    def createToken(self):
        if(not("login" in request.values and "password" in request.values)):
            return errors.eNotLoginOrPassword()

        con = sl.connect('site.db')
        cur = con.cursor()
        obj = cur.execute("SELECT * FROM users WHERE password=? AND name=?", (str(request.values['password']),str(request.values['login']))).fetchall()
        if(len(obj)==1):
            hash_object = hashlib.sha512((str(time.time())+str(obj[0][0])+str(obj[0][1])+str(random.randint(-9999999,9999999))).encode("utf-8"))
            hex_dig = hash_object.hexdigest()
            cur.execute("INSERT INTO tokens (userId,token) VALUES (?,?)",
                              (obj[0][0],hex_dig)).fetchall()
            con.commit()
            return json.dumps({
                "result":{
                    "token":hex_dig
                }
            })

        else:
            return errors.eNotLoginOrPassword()



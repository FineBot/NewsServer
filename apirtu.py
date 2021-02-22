from flask import request
import json
import errors
import sqlite3 as sl
import hashlib
import time
import random
import urllib.parse
import datetime

authorized=False
userId=-1
name=None

class apiClass:
    def __init__(self,method):
        global authorized,name,userId
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
        elif(method=="createArticle"):
            return apiClass.createArticle(self)
        elif (method == "getById"):
            return apiClass.getById(self)
        elif (method == "search"):
            return apiClass.search(self,False)
        elif (method == "searchTags"):
            return apiClass.search(self,True)
        else: return errors.e404()


    def search(self,onlytags):
        print(request.values)
        if (not "keywords" in request.values):
            return errors.eMissing("keywords")
        con = sl.connect('site.db')
        cur = con.cursor()
        result = {"result": []}
        con.create_function("mylower", 1, apiClass.lower_string)
        obj=""
        if(onlytags):
            if(request.values['keywords']=="main"):
                obj = cur.execute(
                    "SELECT * FROM news WHERE main=1 ORDER BY publishedAt DESC LIMIT 0,100").fetchall()
            else:
                obj = cur.execute(
                    "SELECT * FROM news WHERE mylower(tags) LIKE ? ORDER BY publishedAt DESC LIMIT 0,100",
                    ( "%" +urllib.parse.unquote(request.values['keywords']).lower() + "%",)).fetchall()
        else:
            obj = cur.execute(
                "SELECT * FROM news WHERE mylower(title) LIKE ? or mylower(tags) LIKE ? ORDER BY publishedAt DESC LIMIT 0,100",
                ( "%" +urllib.parse.unquote(request.values['keywords']) + "%", "%" + urllib.parse.unquote(request.values['keywords']) + "%")).fetchall()

        if(len(obj)>0):
            for i in range(0, len(obj)):
                result["result"].append({
                    "id": obj[i][0],
                    "title": obj[i][1],
                    "source": obj[i][3],
                    "tags": obj[i][4],
                    "author": obj[i][5],
                    "description": obj[i][6],
                    "coverImage": obj[i][7],
                    "publishedAt": obj[i][8],
                })
        else:
            result={"error":"not found"}
        return json.dumps(result, ensure_ascii=False)


    def getNews(self):
        con = sl.connect('site.db')
        cur=con.cursor()
        result = {"result":{"main":[],"all":[]}}

        obj = cur.execute("SELECT * FROM news WHERE main=1 ORDER BY publishedAt DESC LIMIT 0,100").fetchall()
        for i in range(0, len(obj)):
            result["result"]["main"].append({
                "id": obj[i][0],
                "title": obj[i][1],
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
                "source":obj[i][3],
                "tags":obj[i][4],
                "author":obj[i][5],
                "description":obj[i][6],
                "coverImage":obj[i][7],
                "publishedAt":obj[i][8],
            })
        return json.dumps(result,ensure_ascii=False)

    def getById(self):
        if(not "id" in request.values):
            return errors.eMissing("id")
        con = sl.connect('site.db')
        cur = con.cursor()
        result = {"result": []}

        obj = cur.execute("SELECT * FROM news WHERE id=?",(request.values['id'],)).fetchall()
        if(len(obj)>0):
            result["result"].append({
                "id": obj[0][0],
                "title": obj[0][1],
                "content": obj[0][2],
                "source": obj[0][3],
                "tags": obj[0][4],
                "author": obj[0][5],
                "description": obj[0][6],
                "coverImage": obj[0][7],
                "publishedAt": obj[0][8],
                "dateConvert": (datetime.datetime.utcfromtimestamp(obj[0][8]).strftime('%d.%m.%Y, в %H:%M'))
            })
        else:
            result={"error":"not found"}
        return json.dumps(result,ensure_ascii=False)

    def createArticle(self):
        global authorized,name,userId

        if(not authorized):
            return errors.eNotPermissions()

        args=["title","content","source","tags","description","coverImage","main"]
        for i in range(0,len(args)):
            if(args[i] in request.values):
                if(args[i]=="tags"):
                    try:
                        if (len(json.loads(request.values["tags"])) == 0):
                            return errors.eMissing(args[i])
                    except:
                        return errors.eMissing(args[i])
            else:
                return errors.eMissing(args[i])

        con = sl.connect('site.db')
        cur = con.cursor()
        cur.execute(
            "INSERT INTO news (title,content,source,tags,author,description,coverImage,main,publishedAt) VALUES (?,?,?,?,?,?,?,?,?)",
            (request.values['title'], request.values['content'], request.values['source'], request.values['tags'], name,
             request.values['description'], request.values['coverImage'], request.values['main'], int(time.time())))
        con.commit()
        return json.dumps({"result": 1})


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

    def lower_string(str):
        return str.lower()



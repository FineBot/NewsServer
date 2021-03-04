from flask import request, render_template
import json
import errors
import sqlite3 as sl
import hashlib
import time
import random
import urllib.parse
import datetime
import base64
from flask import send_file

class apiClass:


    def __init__(self,method):
        self['authorized'] = False
        self['userId'] = -1
        self['name'] = None
        if("token" in request.values):
            con = sl.connect('site.db')
            cur = con.cursor()
            obj = cur.execute("SELECT * FROM tokens WHERE token=?",(request.values['token'],)).fetchall()
            if(len(obj)==1):
                self['userId']=obj[0][1]
                self['name']=cur.execute("SELECT * FROM users WHERE id=(?)",(self['userId'],)).fetchall()[0][1]
                self['authorized']=True


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
        elif (method == "checkToken"):
            return apiClass.checkToken(self)
        elif (method == "editArticle"):
            return apiClass.editArticle(self)
        elif(method == "getArticleCover"):
            return apiClass.getArticleCover(self)
        else: return errors.e404()

    def checkToken(self):


        if(self['authorized']):
            return json.dumps({
                "result":{
                    "name":self['name'],
                    "id":self['userId'],
                }
            },ensure_ascii=False)

        else:
            return json.dumps({
                "error":False
            }, ensure_ascii=False)

    def search(self,onlytags):
        print(request.values)
        if (not "keywords" in request.values):
            return errors.eMissing("keywords")

        page = 0
        if ("page" in request.values):
            page = int(request.values['page'])

        con = sl.connect('site.db')
        cur = con.cursor()
        result = {"result": []}
        con.create_function("mylower", 1, apiClass.lower_string)
        obj=""
        if(onlytags):
            if(request.values['keywords']=="main"):
                obj = cur.execute(
                    "SELECT * FROM news WHERE main=1 ORDER BY publishedAt DESC LIMIT 50 OFFSET ?",(page*50,)).fetchall()
            else:
                obj = cur.execute(
                    "SELECT * FROM news WHERE mylower(tags) LIKE ? ORDER BY publishedAt DESC LIMIT 50 OFFSET ?",
                    ( "%" +urllib.parse.unquote(request.values['keywords']).lower() + "%",page*50)).fetchall()
        else:
            if(urllib.parse.unquote(request.values['keywords'])=="*"):
                obj = cur.execute(
                    "SELECT * FROM news ORDER BY publishedAt DESC LIMIT 50 OFFSET ?",(int(page*50),)).fetchall()
            else:
                obj = cur.execute(
                    "SELECT * FROM news WHERE mylower(title) LIKE ? or mylower(tags) LIKE ? ORDER BY publishedAt DESC LIMIT 50 OFFSET ?",
                    ("%" + urllib.parse.unquote(request.values['keywords']).lower() + "%",
                     "%" + urllib.parse.unquote(request.values['keywords']).lower() + "%",page*50)).fetchall()


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
        page=0
        if("page" in request.values):
            page=int(request.values['page'])

        if(page==0):
            obj = cur.execute("SELECT * FROM news WHERE main=1 ORDER BY publishedAt DESC LIMIT 0,25").fetchall()
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

        obj=cur.execute("SELECT * FROM news WHERE main=0 ORDER BY publishedAt DESC LIMIT 50 OFFSET ?",(page*50,)).fetchall()
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
                "main": obj[0][9],
                "dateConvert": (datetime.datetime.utcfromtimestamp(obj[0][8]).strftime('%d.%m.%Y, в %H:%M'))
            })
        else:
            result={"error":"not found"}
        return json.dumps(result,ensure_ascii=False)


    def editArticle(self):
        if (not self['authorized']):
            return errors.eNotPermissions()

        args = ["title", "content", "tags", "description", "main","id"]
        for i in range(0, len(args)):
            if (args[i] in request.values):
                if (args[i] == "tags"):
                    try:
                        if (len(json.loads(request.values["tags"])) == 0):
                            return errors.eMissing(args[i])
                    except:
                        return errors.eMissing(args[i])
                else:
                    if (request.values[args[i]] == '' or request.values[args[i]]=='undefined' or request.values[args[i]]==None):
                        return errors.eMissing(args[i])

            else:
                return errors.eMissing(args[i])

        con = sl.connect('site.db')
        cur = con.cursor()
        cur.execute(
            "UPDATE news SET title=?,content=?,source=?,tags=?,description=?,main=? WHERE id=?",
            (request.values['title'], request.values['content'], request.values['source'], request.values['tags'],
             request.values['description'], request.values['main'], request.values['id']))

        if("coverImage" in request.values):
            cur.execute(
            "UPDATE news SET coverImage=? WHERE id=?",
            (request.values['coverImage'],request.values['id']))
        con.commit()
        return json.dumps({"result": 1})

    def createArticle(self):
        if(not self['authorized']):
            return errors.eNotPermissions()

        args=["title","content","tags","description","coverImage","main"]
        for i in range(0,len(args)):
            if(args[i] in request.values):
                if(args[i]=="tags"):
                    try:
                        if (len(json.loads(request.values["tags"])) == 0):
                            return errors.eMissing(args[i])
                    except:
                        return errors.eMissing(args[i])
                else:
                    if (request.values[args[i]] == '' or request.values[args[i]]=='undefined' or request.values[args[i]]==None):
                        return errors.eMissing(args[i])

            else:
                return errors.eMissing(args[i])

        con = sl.connect('site.db')
        cur = con.cursor()
        cur.execute(
            "INSERT INTO news (title,content,source,tags,author,description,coverImage,main,publishedAt) VALUES (?,?,?,?,?,?,?,?,?)",
            (request.values['title'], request.values['content'], request.values['source'], request.values['tags'], self['name'],
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



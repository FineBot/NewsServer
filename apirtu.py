from typing import io

from flask import request, render_template, make_response
import json
import errors
import sqlite3 as sl
import hashlib
import time
import random
import urllib.parse
import datetime

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

        method=method.lower()
        if(method=="getnews"):
            return apiClass.getNews(self)
        elif(method=="login"):
            return apiClass.createToken(self)
        elif(method=="createarticle"):
            return apiClass.createArticle(self)
        elif (method == "getbyid"):
            return apiClass.getById(self)
        elif (method == "search"):
            return apiClass.search(self,False)
        elif (method == "searchtags"):
            return apiClass.search(self,True)
        elif (method == "checktoken"):
            return apiClass.checkToken(self)
        elif (method == "editarticle"):
            return apiClass.editArticle(self)
        elif (method == "editpassword"):
            return apiClass.EditPass(self)
        elif (method == "editname"):
            return apiClass.EditName(self)
        elif (method == "deletearticle"):
            return apiClass.deleteArticle(self)

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
                    "coverImage": "http://127.0.0.1:15234/getArticleCover?id="+str(obj[i][0]),
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
                    "coverImage": "http://127.0.0.1:15234/getArticleCover?id="+str(obj[i][0]),
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
                "coverImage":"http://127.0.0.1:15234/getArticleCover?id="+str(obj[i][0]),
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
            objA=cur.execute("SELECT name FROM users WHERE id=?",(obj[0][5],)).fetchall()[0][0]

            result["result"].append({
                "id": obj[0][0],
                "title": obj[0][1],
                "content": obj[0][2],
                "source": obj[0][3],
                "tags": obj[0][4],
                "author": objA,
                "description": obj[0][6],
                "coverImage": "http://127.0.0.1:15234/getArticleCover?id="+str(obj[0][0]),
                "publishedAt": obj[0][8],
                "main": obj[0][9],
                "dateConvert": (datetime.datetime.utcfromtimestamp(obj[0][8]).strftime('%d.%m.%Y, в %H:%M'))
            })
        else:
            result={"error":"not found"}
        return json.dumps(result,ensure_ascii=False)


    def checkIn(self,args):
        for i in range(0, len(args)):
            if (args[i] in request.values):
                if (args[i] == "tags"):
                    try:
                        if (len(json.loads(request.values["tags"])) == 0):
                            return errors.eMissing(args[i])
                    except:
                        return errors.eMissing(args[i])
                else:
                    if (request.values[args[i]] == '' or request.values[args[i]]=='undefined' or request.values[args[i]]==None or request.values[args[i]]=="null"):
                        return errors.eMissing(args[i])

            else:
                return errors.eMissing(args[i])
        return None

    def editArticle(self):
        if (not self['authorized']):
            return errors.eNotPermissions()

        ch=apiClass.checkIn(self,["title", "content", "tags", "description", "main","id"])

        if(ch!=None):
            return ch


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

    def deleteArticle(self):
        ch=apiClass.checkIn(self,["id"])
        if (ch != None):
            return ch
        con = sl.connect('site.db')
        cur = con.cursor()


        cur.execute(
            "DELETE FROM news WHERE id=?",
            (request.values['id'],))
        con.commit()
        return json.dumps({"result":1},ensure_ascii=False)


    def createArticle(self):
        if(not self['authorized']):
            return errors.eNotPermissions()


        ch=apiClass.checkIn(self,["title","content","tags","description","coverImage","main"])

        if (ch != None):
            return ch

        con = sl.connect('site.db')
        cur = con.cursor()

        # (data\:[A-Z-a-z\/\;0-9\,\+=]*)

        cur.execute(
            "INSERT INTO news (title,content,source,tags,author,description,coverImage,main,publishedAt) VALUES (?,?,?,?,?,?,?,?,?)",
            (request.values['title'], request.values['content'], request.values['source'], request.values['tags'], self['userId'],
             request.values['description'], request.values['coverImage'], request.values['main'], int(time.time())))
        con.commit()
        return json.dumps({"result": 1})

    def EditName(self):
        if (not "name" in request.values ):
            return errors.eMissing("name")
        if(request.values['name']==''):
            return errors.eMissing("name")

        if(self['authorized']):
            con = sl.connect('site.db')
            cur = con.cursor()

            count=cur.execute("SELECT COUNT(id) FROM users WHERE name=?",(request.values['name'],)).fetchall()[0][0]
            if(count>0):
                return json.dumps({"error":0})



            cur.execute(
                "UPDATE users SET name=? WHERE id=?",
                (request.values['name'], self['userId']))
            con.commit()
            return json.dumps({"result": 1}, ensure_ascii=False)
        else:
            return errors.eNotPermissions()

    def EditPass(self):
        if (not "pass" in request.values):
            return errors.eMissing("id")
        if(request.values['pass']==''):
            return errors.eMissing("pass")

        if(self['authorized']):
            con = sl.connect('site.db')
            cur = con.cursor()
            cur.execute(
                "UPDATE users SET password=? WHERE id=?",
                (request.values['pass'], self['userId']))

            cur.execute(
                "DELETE FROM tokens WHERE userId=? AND NOT token=?",
                (self['userId'], request.values['token']))
            con.commit()

            return json.dumps({"result": 1}, ensure_ascii=False)
        else:
            return errors.eNotPermissions()


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



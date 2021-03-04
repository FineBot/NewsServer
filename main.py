import base64

from flask import Flask, make_response
from flask import request
from flask_cors import CORS
import dbinit
import apirtu
import sqlite3 as sl
import errors

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
dbinit.dbinitClass()


def getArticleCover(self):
    if ("id" in request.values):
        pass
    else:
        errors.eMissing("id")
    con = sl.connect('site.db')
    cur = con.cursor()
    img = cur.execute(
        "SELECT coverImage from news WHERE id=?",
        (request.values['id'],)).fetchall()[0][0]
    response = make_response(base64.b64decode(img.split(",")[1]))
    response.headers.set('Content-Type', img.split(",")[0].split(";")[0].replace("data:", ""))
    return response

@app.route('/<method>',methods=["POST"])
def first(method):
    return apirtu.apiClass.__init__({"authorized":False},method)

@app.route('/<method>',methods=["GET"])
def first1(method):
    if(method.lower()=="getarticlecover"):
        return getArticleCover(None)
    return errors.eOnlyPost()

@app.errorhandler(404)
def page_not_found(error):
    return errors.e404()

@app.errorhandler(500)
def error(error):
    return errors.e500()

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=15234)
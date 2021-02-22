from flask import Flask
from flask import request
from flask_cors import CORS
import dbinit
import apirtu
import errors

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
dbinit.dbinitClass()

@app.route('/<method>',methods=["POST"])
def first(method):
    return apirtu.apiClass.__init__(None,method)

@app.route('/<method>',methods=["GET"])
def first1(method):
    return errors.eOnlyPost()

@app.errorhandler(404)
def page_not_found(error):
    return errors.e404()

@app.errorhandler(500)
def error(error):
    return errors.e500()

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=15234)
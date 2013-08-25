import os
from flask import Flask

app= Flask(__name__)

@app.route('/')
def hello():
    return '<img src="http://clug.kr/~elwlwlwk/holo.png" />'

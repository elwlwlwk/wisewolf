import os
from flask import Flask

app= Flask(__name__)

@app.route('/')
def hello():
    return '<img width="100%" src="http://clug.kr/~elwlwlwk/holo.png" />'

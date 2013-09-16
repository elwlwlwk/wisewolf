import os
from flask import Flask, render_template

app= Flask(__name__)
app.secret_key= os.urandom(24)
app.debug= True

@app.route('/')
@app.route('/index')
def hello():
    return render_template('index.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/login', methods=['POST','GET'])
def login():
    return render_template('login.html')

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8080)

import os
from flask import Flask, render_template, g, request, session, redirect, url_for
import sqlite3
from contextlib import closing
import member
import psycopg2

DEBUG= True
SECRET_KEY= os.urandom(24)

app= Flask(__name__)
app.secret_key= os.urandom(24)
app.debug= False 
app.config.from_object(__name__)

con= None
@app.before_request
def before_request():
	con= psycopg2.connect(database='holo', user='wisewolf')
	g.db= con.cursor()

@app.teardown_request
def teardown_request(exception):
	if con:
		con.close()
	
@app.route('/index')
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/signin', methods=['POST','GET'])
def signin():
	if request.method== 'POST':
		if member.signin_validation(request.form['username'], request.form['password'])== True:
			session['signed_in']=True
			session['user']= request.form['username']
			return redirect(url_for('index'))
	return render_template('signin.html')

@app.route('/signout')
def signout():
	session.pop('signed_in', None)
	session.pop('user', None)
	return redirect(url_for('index'))

@app.route('/signup', methods=['POST','GET'])
def signup():
	if request.method== 'POST':
		if member.new_member(request.form['username'], request.form['password'],\
request.form['email'])== True:
			return redirect(url_for('signin'))
		else:
			return redirect(url_for('signup'))
	return render_template('signup.html')

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8080)

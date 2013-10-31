import os
from flask import Flask, render_template, g, request, session, redirect, url_for, make_response
import sqlite3
from contextlib import closing
import psycopg2

app= Flask(__name__)
config_loc='DEV'

# config flask app
if('config.py' in os.listdir('./')):
	import config
	app.config.from_object('config.DevelopmentConfig')
else:
	config_loc='SERV'
	app.secret_key= os.urandom(24)
	app.debug= False
	app.config.from_object(__name__)

# make database connection
con= None

@app.before_request
def before_request():
	if config_loc == 'DEV':
		con= psycopg2.connect(database='holo', user='wisewolf')
	if config_loc == 'SERV':
		con= psycopg2.connect(database='deh17pgu09nikp', user='wjfzhcasmhewjw',\
password='8qMA0A33WirYdrnV5erw9DRiAY',\
host='ec2-54-227-251-13.compute-1.amazonaws.com', port='5432')
	g.db= con.cursor()

# disconnect database
@app.teardown_request
def teardown_request(exception):
	if con:
		con.close()

# make url mapping
def make_url_mapping():
	import views
	app.add_url_rule('/', view_func= views.RenderTemplateView.as_view('root',\
template_name='index.html'))
	app.add_url_rule('/index', view_func= views.RenderIndex.as_view('index'))

	app.add_url_rule('/profile',\
view_func= views.RenderTemplateView.as_view('profile',\
template_name='profile.html'))

	app.add_url_rule('/signin', view_func= views.RenderSignin.as_view('signin',\
template_name='signin.html'))

	app.add_url_rule('/signout',\
view_func= views.RenderSignout.as_view('signout'))

	app.add_url_rule('/signup', view_func= views.RenderSignup.as_view('signup',\
template_name='signup.html'))

make_url_mapping()

@app.route('/gallery')
def gallery():
	from flask import flash
	img_list= os.listdir('./imgs')
	for img in img_list:
		flash(img)
	return render_template("gallery.html") 

@app.route("/imgs/<path:path>")
def images(path):
    fullpath = "./imgs/" + path
    resp = make_response(open(fullpath).read())
    resp.content_type = "image/jpeg"
    return resp

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8000, debug= True)

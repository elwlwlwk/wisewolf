import os
from flask import Flask, render_template, g, request, session, redirect, url_for, make_response
import sqlite3
from contextlib import closing
import psycopg2
from redis_session import RedisSessionInterface

app= Flask(__name__)
config_loc='DEV'

# config flask app
if('config.py' in os.listdir('./')):
	import config
	app.config.from_object('config.DevelopmentConfig')
else:
	app.session_interface= RedisSessionInterface()
	config_loc='SERV'
	app.secret_key= os.urandom(24)
	app.debug= False
	app.config.from_object(__name__)

# make database connection
con= None

@app.before_request
def before_request():
	con= psycopg2.connect(database='wisewolf', user='elwlwlwk',\
password='dlalsrb3!',\
host='165.194.104.192')
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
	gen_thumb()
	img_list= os.listdir('./imgs/thumbgen')
	for img in img_list:
		flash(img)
	return render_template("gallery.html") 

@app.route("/imgs/<path:path>")
def images(path):
	gen_thumb()
	fullpath = "./imgs/" + path
	resp = make_response(open(fullpath).read())
	resp.content_type = "image/jpeg"
	return resp

def gen_thumb():
	from PIL import Image
	img_list= os.listdir('./imgs')
	img_list.remove('thumbnail')
	img_list.remove('thumbgen')
	if(len(img_list)== 0):
		return
	size= 150, 150
	for img in img_list:
		try:
			im= Image.open('./imgs/'+img)	
			im.thumbnail(size, Image.ANTIALIAS)
			im.save('./imgs/thumbnail/'+img)
			os.system('mv ./imgs/'+img+' ./imgs/thumbgen')
		except IOError, e:
			print e	

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=6974)
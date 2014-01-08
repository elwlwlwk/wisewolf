import os
from flask import render_template, g, request, session, redirect, url_for, make_response
import sqlite3
from contextlib import closing
import psycopg2
from redis_session import RedisSessionInterface
from wisewolf.web import app


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

from datetime import timedelta
CHATTING_ROOM_EXPIRE= timedelta(hours=24)

@app.route('/chatting/<path:path>')
def chattingroom(path):
#	print "path: "+path
	if path =='new':
		import os
		import binascii
		import time
		room_id= str(int(time.time()))+binascii.b2a_hex(os.urandom(8))
		return redirect("/chatting/"+room_id)
	prefix= "chat_room:"
	from redis import Redis
	r= Redis(db=1)
	val= r.get(prefix+path)
	if val is not None:
		enter_existing_room()
	else:
		create_new_room(r, prefix, path)
	return render_template("chatting_room.html")
	
def enter_existing_room():
	pass
def create_new_room(r, prefix, path):
	r.setex(prefix + path, '',\
int(CHATTING_ROOM_EXPIRE.total_seconds()))

	
@app.route('/gallery')
def gallery():
	from flask import flash
	gen_thumb()
	img_list= os.listdir('./wisewolf/web/imgs/thumbgen')
	for img in img_list:
		flash(img)
	return render_template("gallery.html") 

@app.route("/imgs/<path:path>")
def images(path):
	gen_thumb()
	fullpath = "./wisewolf/web/imgs/" + path
	resp = make_response(open(fullpath).read())
	resp.content_type = "image/jpeg"
	return resp

def gen_thumb():
	from PIL import Image
	img_list= os.listdir('./wisewolf/web/imgs')
	img_list.remove('thumbnail')
	img_list.remove('thumbgen')
	if(len(img_list)== 0):
		return
	size= 150, 150
	for img in img_list:
		try:
			im= Image.open('./wisewolf/web/imgs/'+img)
			im.thumbnail(size, Image.ANTIALIAS)
			im.save('./wisewolf/web/imgs/thumbnail/'+img)
			os.system('mv ./wisewolf/web/imgs/'+img+' ./wisewolf/web/imgs/thumbgen')
		except IOError, e:
			print e	

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=6974)

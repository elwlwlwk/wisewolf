import os
from flask import render_template, g, request, session, redirect, url_for, make_response
import sqlite3
from contextlib import closing
import psycopg2
from redis_session import RedisSessionInterface
from wisewolf.web import app
from wisewolf.websocket.chatting import redis_RoomSession
from wisewolf.websocket import Mongo_Wisewolf

from pymongo import MongoClient
import json
from flask import Markup

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
	g.mongo= Mongo_Wisewolf

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

@app.route('/versuschat/<path:path>')
def One2OneRoom(path):
#	print "path: "+path
	if path =='new':
		import os
		import binascii
		import time
		room_id= str(int(time.time()))+binascii.b2a_hex(os.urandom(8))
		return redirect("/versuschat/"+room_id)
	prefix= "versus_chat:"
	r= redis_RoomSession
	val= r.get(prefix+path)
	if val is not None:
		enter_existing_room()
	else:
		create_new_room(r, prefix, path)
	return render_template("versuschat.html")

@app.route('/chatting/<path:path>', methods=['POST','GET'])
def chattingroom(path):
#	print "path: "+path
	if path =='new':
		import os
		import binascii
		import time
		room_id= str(int(time.time()))+binascii.b2a_hex(os.urandom(8))
		return redirect("/chatting/"+room_id)
	prefix= "chat_room:"
	r= redis_RoomSession
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

@app.route("/test")
def hen():
	return render_template("test.html")

@app.route("/base/<path:path>")
def base(path):
	return render_template(path)

@app.route("/files")
def files():
	from flask import flash
	gen_thumb()
	file_list= os.listdir('./wisewolf/web/file')
	file_list.sort()
	for myfile in file_list:
		flash(myfile)
	return render_template("files.html") 

@app.route("/file/<path:path>")
def file(path):
	gen_thumb()
	fullpath = "./wisewolf/web/file/" + path
	resp = make_response(open(fullpath).read())
	resp.content_type = "application/octet-stream"
	return resp

@app.route("/popup/<path:path>")
def popup(path):
	return render_template("popup/"+path);

@app.route('/vote', methods=['POST'])
def vote():
	if session.has_key('user')!= True:
		try:
			return json.dumps(g.mongo.rooms.find_one({"room_seq":request.form['tag_room']})['tags'])
		except TypeError, e:
			return ''

	room= g.mongo.rooms.find_one({"room_seq":request.form['tag_room']})
	def vote_tag(pros_cons, new_tag= True):
		updated= True
		if new_tag== True:
			updated= False
		room_tags= room['tags']
		for tag in room_tags:
			if tag['tag']== dest_tag:
				if pros_cons== "up":
					tag['up']+=1
				else:
					tag['down']+=1
				updated= True
				break;
		if updated== False:
			room_tags.append({'tag':dest_tag, 'up':1, 'down':0})
		g.mongo.rooms.update({"room_seq":request.form['tag_room']},{"$set":{"tags":room_tags}})

		pass
	prefix= "chat_room:"
	if request.form['tag_type']== 'new':
		dest_tag= Markup.escape(request.form['dest_tag'].replace(" ","").strip())
		if room is None:
			return ''
		else:# if exist room
			if len(dest_tag) is not 0:
				if room.has_key('tags'):# if room already has tag, vote up the tag
					vote_tag("up")
				else:
					g.mongo.rooms.update({"room_seq":request.form['tag_room']},{"$set":{"tags":[{'tag':dest_tag, 'up':1, 'down':0}]}})
			return json.dumps(g.mongo.rooms.find_one({"room_seq":request.form['tag_room']})['tags'])
	elif request.form['tag_type']== 'vote':
		dest_tag= request.form['dest_tag'].replace(" ","").strip()
		vote_tag(request.form['pros_cons'], new_tag= False)
		return json.dumps(g.mongo.rooms.find_one({"room_seq":request.form['tag_room']})['tags'])

	
if __name__ == '__main__':
	app.run(host='0.0.0.0', port=6974)

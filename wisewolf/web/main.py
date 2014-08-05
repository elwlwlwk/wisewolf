import os
from flask import render_template, g, request, session, redirect, url_for, make_response, flash, abort
import sqlite3
from contextlib import closing
from datetime import timedelta
from wisewolf.web.redis_session import RedisSessionInterface
from wisewolf.web import app
from wisewolf.db_pool import Mongo_Wisewolf, redis_RoomSession, Psql_Cursor
from wisewolf.web.vote import vote_tag, get_tag_status
import wisewolf.web.search_room as search_room
import binascii
import time
import wisewolf.web.views as views
import wisewolf.web.config

from pymongo import MongoClient
import json
from flask import Markup

config_loc='DEV'

# config flask app
if('config.py' in os.listdir('./')):
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
	g.db= Psql_Cursor
	g.mongo= Mongo_Wisewolf
	try:
		print(request.headers["X-Real-Ip"]+": "+request.headers["Referer"])
	except:
		pass

# disconnect database
@app.teardown_request
def teardown_request(exception):
	if con:
		con.close()

@app.errorhandler(404)
def notfound(error):
	return "Not found... What r u doing?"

@app.errorhandler(405)
def invalid_request(error):
	return "Please do not attack my castle. Go away!"

@app.errorhandler(501)
def not_implemeted(error):
	return "Not implemeted yet. sry"
	
# make url mapping
def make_url_mapping():
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

CHATTING_ROOM_EXPIRE= timedelta(hours=24)

@app.route('/room_search', methods=['POST', 'GET'])
def room_search():
	r= redis_RoomSession
	room_list= r.keys()
	room_list.sort(reverse= True)
	return render_template("room_search.html")

@app.route('/get_room_info', methods=['POST'])
def get_room_info():
	try:
		info_request= request.get_json(force=True)

		req_room_seq= info_request["room_seq"]
		result= g.mongo.rooms.find_one({"room_seq":req_room_seq})

		tag_list= g.mongo.tags.find({"room_list.room_seq": req_room_seq})
		tags=[]
		for tag in tag_list:
			for room in tag["room_list"]:
				if room["room_seq"]== req_room_seq:
					tags.append({"tag":tag["tag"],"up":room["up"],"down":room["down"]})

		if result is None:
			return '{}'
		result.pop("_id")
		result["tags"]= tags
		return json.dumps(result)
	except Exception as e:
		print(e)
		return '{}'

@app.route('/get_room_list', methods=['POST'])
def get_room_list():
	return search_room.search_room(request)
	
@app.route('/chatting/<path:path>', methods=['POST','GET'])
def chattingroom(path):
#	print "path: "+path
	r= redis_RoomSession
	val= g.mongo.rooms.find_one({"room_seq":path},{"_id":1, "room_kind":1})

	if path =='new':
		if request.method!= 'POST':
			abort(405)
		room_id= str(int(time.time()))+binascii.b2a_hex(os.urandom(8)).decode("utf-8")
		create_new_room(r, room_id, request)
		return redirect("/chatting/"+room_id)
	if val is not None:
		enter_existing_room()
	else:
		abort(405)
	g.room_id=path
	if val["room_kind"]== "generic":
		return render_template("chatting_room.html")
	elif val["room_kind"]== "versus":
		return render_template("versuschat.html")
	else:
		abort(501)

def enter_existing_room():
	pass

def create_new_room(r, room_id, request):
	max_participants= request.form["participants"]
	try:
		max_participants= int(max_participants)
	except:
		max_participants= ''
	room_info={"room_kind":request.form["room_kind"], "room_title":Markup.escape(request.form["title"]),
"max_participants":max_participants, "cur_participants":0, "open_time":str(time.time())}
	r.setex(room_id, json.dumps(room_info), int(CHATTING_ROOM_EXPIRE.total_seconds()))
	
	room_data={"room_seq":room_id, "room_title": room_info["room_title"], "room_kind": room_info["room_kind"],
"open_time": room_info["open_time"], "max_participants": room_info["max_participants"],
"voted_members":[]}
	g.mongo.rooms.insert(room_data)

	print("create new room")
	if g.mongo.tags.update({"tag":"tag_me"},{"$addToSet":{"room_list":{"room_seq":room_id, "up":0, "down":0}}})["updatedExisting"]== False:
		g.mongo.tags.insert({"tag":"tag_me", "room_list":[{"room_seq":room_id, "up":0, "down":0}]})
	if request.form["room_kind"]== "versus":
		room_info["room_kind"]="versus_supportA"
		r.setex(room_id+"_supportA", json.dumps(room_info), int(CHATTING_ROOM_EXPIRE.total_seconds()))
		room_info["room_kind"]="versus_supportB"
		r.setex(room_id+"_supportB", json.dumps(room_info), int(CHATTING_ROOM_EXPIRE.total_seconds()))

@app.route('/gallery')
def gallery():
	gen_thumb()
	img_list= os.listdir('./wisewolf/web/imgs/thumbgen')
	for img in img_list:
		flash(img)
	return render_template("gallery.html") 

@app.route('/secrete_gall')
def secrete_gallery():
	encrypt_image()
	img_list= os.listdir('./wisewolf/web/encrypt_imgs')
	for img in img_list:
		flash(img)
	return render_template("secrete_gall.html") 

@app.route('/videos/<path:path>')
def videos(path):
	print(path)
	flash(path)
	return render_template("video.html") 

@app.route("/video/<path:path>")
def vidoe(path):
	fullpath = "./wisewolf/web/videos/" + path
	resp = make_response(open(fullpath,"rb").read())
	return resp

@app.route("/imgs/<path:path>")
def images(path):
	gen_thumb()
	fullpath = "./wisewolf/web/imgs/" + path
	resp = make_response(open(fullpath,"rb").read())
	resp.content_type = "image/jpeg"
	return resp

@app.route("/encrypt_imgs/<path:path>")
def encrypt_images(path):
	encrypt_image()
	fullpath = "./wisewolf/web/encrypt_imgs/" + path
	resp = make_response(open(fullpath,"rb").read())
	resp.content_type = "text/html"
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
		except IOError as e:
			print(e)

def encrypt_image():
	os.chdir("./wisewolf/web/encrypt_imgs")
	file_list= os.listdir(".")
	base_list=[]
	
	for f in file_list:
		if "html" in f:
			continue	
		base_list.append(f.split(".")[0]+".base")
		os.system("base64 "+f+" > "+f.split(".")[0]+".base")
		os.system("rm "+f)
	print(base_list)
	
	for b in base_list:
		f= open(b,'r')
		print("")
		try:
			key= session["user"]
		except Exception as e:
			key= ""
		
		code="<script>var key='"+key+"'</script><img src=\"data:image/png;base64,"
		code+= f.read()
		#code= code.replace("T","TrixlnxSegEzusp")
		#code= code.replace("YGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBg","TriWA0R1F3YVneri")
		#code= code.replace("YGBg","TefisEfaVBxSe4Wgdj25E")
		#code= code.replace("+","gE4sZetEwgdDFsfo36Sef")
		#code= code.replace("AwMD","gE4sZetweoZvn6Sef")
		#code= code.replace("9j","eWixE2ovZoskeWfel")
		#code= code.replace("A","EwgAevZsbdEhseeAW35")
		#code= code.replace("e", "eagHweZsee44w6E")
		#code= code.replace("Ew","EhwBe8hTdb2ReyS")
		code+="\" />"
		newf= open(b.split(".")[0]+".html","w")
		newf.write(code)
		f.close()
		newf.close()

	os.system("rm *.base")
	os.chdir("../../..")

@app.route("/test")
def hen():
	return render_template("test.html")

@app.route("/base/<path:path>")
def base(path):
	return render_template(path)

@app.route("/files")
def files():
	gen_thumb()
	file_list= os.listdir('./wisewolf/web/file')
	file_list.sort()
	for myfile in file_list:
		flash(myfile)
	return render_template("files.html") 

@app.route("/file/<path:path>")
def file_down(path):
	gen_thumb()
	fullpath = "./wisewolf/web/file/" + path
	resp = make_response(open(fullpath, "rb").read())
	resp.content_type = "application/octet-stream"
	return resp

@app.route("/popup/<path:path>")
def popup(path):
	return render_template("popup/"+path);

@app.route('/vote', methods=['POST'])
def vote():
	room_seq= request.form["tag_room"].replace("#","")
	tag_status={}
	voted= False
	if "user" in session:
		if request.form['tag_type']== 'new':
			dest_tag= Markup.escape(request.form['dest_tag'].replace(" ","").strip())
			if len(dest_tag) is not 0:
				vote_tag(room_seq, dest_tag, "up")
		elif request.form['tag_type']== 'vote':
			dest_tag= request.form['dest_tag'].replace(" ","").strip()
			vote_tag(room_seq, dest_tag, request.form['pros_cons'], new_tag= False)
	tag_status= get_tag_status(room_seq)
	if "user" in session and session["user"] in tag_status["voted_members"]:
		voted= True
	return json.dumps({"tags":tag_status["tags"],"voted":voted})

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=6974)

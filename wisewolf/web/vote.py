from flask import g, session
from wisewolf.common import MongoDao

def vote_tag(room_seq, dest_tag, pros_cons, new_tag= True):
	room= g.MongoDao.find_room(room_seq)
	voted_members= room["voted_members"]
	if dest_tag== "tag_me" or session["user"] in voted_members:
		return
	room= g.MongoDao.find_room(room_seq)
	tag= g.MongoDao.find_tag(dest_tag)
	if tag is None:
		g.MongoDao.insert_tag(dest_tag, room_seq, 1, 0)
	else:
		vote_list= tag["room_list"]
		room_exists= False
		for vote in vote_list:
			if vote["room_seq"]== room_seq:
				vote[pros_cons]+= 1
				room_exists= True
				break
		if room_exists== True:
			g.MongoDao.update_tag(dest_tag, vote_list)
		else:	
			g.MongoDao.add_room_to_tag(dest_tag,room_seq, 1, 0)
	if session["user"]== "elwlwlwk":
		return
	g.MongoDao.add_voted_user(room_seq,session["user"])

def get_tag_status(room_seq):
	result={}
	result["tags"]=[]
	try:
		result["voted_members"]= g.MongoDao.find_room(room_seq,{"voted_members":1})
	except Exception as e:
		result["voted_members"]=[]
	tags= g.MongoDao.get_room_tag_list(room_seq)
	for tag in tags:
		for vote in tag["room_list"]:
			if vote["room_seq"]== room_seq:
				result["tags"].append({"tag":tag["tag"],"up":vote["up"],"down":vote["down"]})
				break
	return result

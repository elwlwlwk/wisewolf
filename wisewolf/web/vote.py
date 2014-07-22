from flask import g, session
def vote_tag(room_seq, dest_tag, pros_cons, new_tag= True):
	room= g.mongo.rooms.find_one({"room_seq":room_seq})
	voted_members= room["voted_members"]
	if dest_tag== "tag_me" or session["user"] in voted_members:
		return
	room= g.mongo.rooms.find_one({"room_seq":room_seq})
	tag= g.mongo.tags.find_one({"tag":dest_tag})
	if tag is None:
		g.mongo.tags.insert({"tag":dest_tag,"room_list":[{"room_seq":room_seq, "up":1, "down":0}]})
	else:
		vote_list= tag["room_list"]
		room_exists= False
		for vote in vote_list:
			if vote["room_seq"]== room_seq:
				vote[pros_cons]+= 1
				room_exists= True
				break
		if room_exists== True:
			g.mongo.tags.update({"tag":dest_tag},{"$set":{"room_list":vote_list}})
		else:	
			g.mongo.tags.update({"tag":dest_tag},{"$addToSet":{"room_list":{"room_seq":room_seq, "up":1, "down":0}}})
	g.mongo.rooms.update({"room_seq":room_seq},{"$addToSet":{"voted_members":session["user"]}})

def get_tag_status(room_seq):
	result={}
	result["tags"]=[]
	try:
		result["voted_members"]= g.mongo.rooms.find_one({"room_seq":room_seq},{"voted_members":1})["voted_members"]
	except Exception as e:
		result["voted_members"]=[]
	tags= g.mongo.tags.find({"room_list.room_seq":room_seq})
	for tag in tags:
		for vote in tag["room_list"]:
			if vote["room_seq"]== room_seq:
				result["tags"].append({"tag":tag["tag"],"up":vote["up"],"down":vote["down"]})
				break
	return result

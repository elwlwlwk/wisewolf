from flask import g, session
def vote_tag(room_seq, dest_tag, pros_cons, new_tag= True):
	room= g.mongo.rooms.find_one({"room_seq":room_seq})
	voted_members= room["voted_members"]
	if session["user"] in voted_members:
		return
	voted_members.append(session["user"])
	updated= True
	if new_tag== True:
		updated= False

	room_tags= room['tags']
	vote_count=0 #to disable vote_me tag
	for tag in room_tags:
		vote_count+= tag['up']
		if tag['tag']== dest_tag and tag['tag']!= "tag_me":
			if pros_cons== "up":
				tag['up']+=1
			else:
				tag['down']+=1
			updated= True
	if vote_count>=15 and room_tags[0]["tag"]== "tag_me":
		poped_tag= room_tags.pop(0)
			
	if updated== False:
		room_tags.append({'tag':dest_tag, 'up':1, 'down':0})
	g.mongo.rooms.update({"room_seq":room_seq},{"$set":{"tags":room_tags,"voted_members":voted_members}})

def get_tag_status(room_seq):
	room= g.mongo.rooms.find_one({"room_seq":room_seq})
	return room

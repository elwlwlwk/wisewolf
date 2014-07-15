from wisewolf.db_pool import redis_RoomSession, Mongo_Wisewolf
import json
from flask import Markup

def search_room(request):
	search_request={}
	try:
		search_request= request.get_json(force=True)
	except:
		return '{}'
	
	search_mode= json.loads(search_request["search_mode"])
	keyword= Markup.escape(search_request["keyword"])
	req_seq= search_request['seq']-1

	result={}
	result['room_info']=[]

	if search_mode["search_by"]== "title":
		r= redis_RoomSession
		room_list= r.keys()
		room_list.sort(reverse= True)
	
		result_counter=0
		for key in [x.decode() for x in room_list]:
			if 'support' in key:
				continue
			if result_counter>=int(req_seq)+20:
				break
			room= json.loads(r.get(key).decode("utf-8"))
			if keyword in room["room_title"]:
				result_counter+=1
				if result_counter> req_seq:
					try:
						result['room_info'].append({"key":key, "title":room["room_title"],"cur_participants":room["cur_participants"],
	"max_participants":(lambda x: '*' if x=='' else x)(room["max_participants"])})
					except:
						result['room_info'].append(room_info= {"key":"error", "title":"error", "max_participants":"error", "cur_participants":"error"})
		return json.dumps(result)
	else:
		room_collection= Mongo_Wisewolf.rooms
		result_list= room_collection.find({"tags.tag":keyword}).sort("_id",-1).skip(req_seq).limit(20)
		for room in result_list:
			result['room_info'].append({"key":room["room_seq"], "title":room["room_title"],"cur_participants":"0",
	"max_participants":(lambda x: '*' if x=='' else x)(room["max_participants"])})
		return json.dumps(result)

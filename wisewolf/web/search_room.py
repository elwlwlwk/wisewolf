from wisewolf.db_pool import redis_RoomSession
import json
from flask import Markup

def search_room(request):
	search_request={}
	try:
		search_request= request.get_json(force=True)
	except:
		return '{}'
	r= redis_RoomSession
	room_list= r.keys()
	room_list.sort(reverse= True)
	result={}
	result['room_info']=[]

	result_counter=0
	for key in room_list:
		if 'support' in key:
			continue
		if result_counter>=int(search_request['seq'])+20:
			break
		room= json.loads(r.get(key))
		if Markup.escape(search_request["keyword"]) in room["room_title"]:
			result_counter+=1
			if result_counter>= search_request['seq']:
				try:
					result['room_info'].append({"key":key, "title":room["room_title"],"cur_participants":room["cur_participants"],
"max_participants":(lambda x: '*' if x=='' else x)(room["max_participants"])})
				except:
					result['room_info'].append(room_info= {"key":"error", "title":"error", "max_participants":"error", "cur_participants":"error"})
	return json.dumps(result)

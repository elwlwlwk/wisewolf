from wisewolf.db_pool import redis_RoomSession, Mongo_Wisewolf
from wisewolf.common import MongoDao
import json
from flask import Markup

from re import escape as re_escape

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

	result_list= get_list_from_mongo(keyword, search_mode, req_seq)
	for room in result_list:
		try:
			result['room_info'].append({"key":room["room_seq"], "title":room["room_title"],"cur_participants":"0",
"max_participants":(lambda x: '*' if x=='' else x)(room["max_participants"])})
		except:
			print("Exception: search_room.search_room:",e)
			result['room_info'].append({"key":"error", "title":"error", "max_participants":"error", "cur_participants":"error"})
	return json.dumps(result)

def get_list_from_mongo(keyword, search_mode, req_seq):
	if search_mode["search_by"]== "tag":
		return MongoDao.Mongo_search_room_by_tag(keyword, search_mode, req_seq)
	elif search_mode["search_by"]== "title":
		try:
			return Mongo_Wisewolf.rooms.find({"room_title":{"$regex":"(?i).*"+re_escape(keyword)+".*"}}).sort("_id",-1).skip(req_seq).limit(20)
		except Exception as e:
			print("Exception: search_room.get_list_from_mongo:",e)
			return []

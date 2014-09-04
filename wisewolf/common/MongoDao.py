from wisewolf.db_pool import Mongo_Wisewolf

class MongoDao:
	def __init__(self):
		self.db= Mongo_Wisewolf
	
	def Mongo_search_room_by_tag(self,keyword="", search_mode={}, order= 1, req_seq=0, limit=20):
		if search_mode["order_by"]== "time":
			try:
				room_list= Mongo_Wisewolf.tags.find_one({"tag":keyword},{"room_list.room_seq":1})["room_list"]
			except TypeError as e:
				return []
			room_seq_list=[]
			for room in room_list:
				room_seq_list.append(room["room_seq"])
			return Mongo_Wisewolf.rooms.find({"room_seq":{"$in":room_seq_list}}).sort("_id",-1).skip(req_seq).limit(20)

		elif search_mode["order_by"]== "vote":
			pass
		return []


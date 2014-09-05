from wisewolf.db_pool import Mongo_Wisewolf

class MongoDao:
	def __init__(self):
		self.db= Mongo_Wisewolf
	
	def Mongo_search_room_by_tag(self,keyword="", search_mode={}, req_seq=0, limit=20):
		try:
			room_list= Mongo_Wisewolf.tags.find_one({"tag":keyword},{"room_list.room_seq":1, "room_list.up":1})["room_list"]
			if search_mode["order_by"]== "time":
				room_seq_list=[]
				for room in room_list:
					room_seq_list.append(room["room_seq"])
				return Mongo_Wisewolf.rooms.find({"room_seq":{"$in":room_seq_list}}).sort("_id",-1).skip(req_seq).limit(limit)

			elif search_mode["order_by"]== "vote":
				room_list.sort(key= lambda r: r["up"], reverse= True)
				room_seq_list=[]
				for room in room_list:
					room_seq_list.append(room["room_seq"])

				result= Mongo_Wisewolf.rooms.find({"room_seq":{"$in":room_seq_list[req_seq:req_seq+limit]}}).limit(limit)
				result_list=[]
				for r in result:
					r['sort_order']=room_seq_list.index(r['room_seq'])
					result_list.append(r)
				result_list.sort(key= lambda r: r["sort_order"])
				return result_list
		except Exception as e:
			print("Exception: MongoDao.MongoDao.Mongo_search_room_by_tag:",e)
			return []


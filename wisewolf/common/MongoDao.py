from wisewolf.db_pool import Mongo_Wisewolf

from re import escape as re_escape

class MongoDao:
	def __init__(self, db=Mongo_Wisewolf):
		self.db= db
	
	def search_room_by_tag(self,keyword="", search_mode={}, req_seq=0, limit=20):
		try:
			room_list= self.db.tags.find_one({"tag":keyword},{"room_list.room_seq":1, "room_list.up":1})["room_list"]
			if search_mode["order_by"]== "time":
				room_seq_list=[]
				for room in room_list:
					room_seq_list.append(room["room_seq"])
				return self.db.rooms.find({"room_seq":{"$in":room_seq_list}}).sort("_id",-1).skip(req_seq).limit(limit)

			elif search_mode["order_by"]== "vote":
				room_list.sort(key= lambda r: r["up"], reverse= True)
				room_seq_list=[]
				for room in room_list:
					room_seq_list.append(room["room_seq"])

				result= self.db.rooms.find({"room_seq":{"$in":room_seq_list[req_seq:req_seq+limit]}}).limit(limit)
				result_list=[]
				for r in result:
					r['sort_order']=room_seq_list.index(r['room_seq'])
					result_list.append(r)
				result_list.sort(key= lambda r: r["sort_order"])
				return result_list
		except Exception as e:
			print("Exception: MongoDao.MongoDao.Mongo_search_room_by_tag:",e)
			return []
	
	def search_room_by_title(self, keyword="", search_mode={}, req_seq=0, limit=20):
		try:
			return Mongo_Wisewolf.rooms.find({"room_title":{"$regex":"(?i).*"+re_escape(keyword)+".*"}, "room_kind":{"$ne":"support"}}).sort("_id",-1).skip(req_seq).limit(20)
		except Exception as e:
			print("Exception: MongoDao.MongoDao.Mongo_search_room_by_title:",e)
			return []

	def get_room_tag_list(self, room_seq):
		try:
			return self.db.tags.find({"room_list.room_seq": room_seq})
		except Exception as e:
			print("Exception: MongoDao.MongoDao.Mongo_search_room_by_title:",e)
			return []
	
	def find_room(self, room_seq, projection= None):
		try:
			return self.db.rooms.find_one({"room_seq":room_seq}, projection)
		except Exception as e:
			print("Exception: MongoDao.MongoDao.find_room:",e)
			return []
	
	def find_chat(self, room_seq, projection= None):
		try:
			return self.db.chat_log.find_one({"room_seq":room_seq}, projection)
		except Exception as e:
			print("Exception: MongoDao.MongoDao.find_chat:",e)
			return []
	
	def insert_chat(self, room_seq, chat_log):
		try:
			return self.db.chat_log.insert({"room_seq":room_seq, "chat_log":chat_log})
		except Exception as e:
			print("Exception: MongoDao.MongoDao.insert_chat:",e)
			return []

	def add_chat(self, room_seq, message):
		try:
			return self.db.chat_log.update({"room_seq":room_seq},{"$addToSet":{"chat_log":message}})
		except Exception as e:
			print("Exception: MongoDao.MongoDao.add_chat:",e)
			return []
	
	def insert_room(self, room_data):
		try:
			if "room_seq" in room_data and "room_title" in room_data and "room_kind" in room_data and "open_time" in room_data and "out_dated" in room_data:
				return self.db.rooms.insert(room_data)
			else:
				raise KeyError("insufficient key")
		except Exception as e:
			print("Exception: MongoDao.MongoDao.insert_room:",e)
			return []
	
	def update_tag(self, tag, room_list):
		try:
			return self.db.tags.update({"tag":tag},{"$set":{"room_list":room_list}})
		except Exception as e:
			print("Exception: MongoDao.MongoDao.update_tag:",e)
			return []
	
	def add_room_to_tag(self, tag, room_seq, up, down):
		try:
			return self.db.tags.update({"tag":tag},{"$addToSet":{"room_list":{"room_seq":room_seq, "up":up, "down":down}}})
		except Exception as e:
			print("Exception: MongoDao.MongoDao.add_room_to_tag:",e)
			return []

	def insert_tag(self, tag, room_seq, up, down):
		try:
			return self.db.tags.insert({"tag":tag, "room_list":[{"room_seq":room_seq, "up":up, "down":down}]})
		except Exception as e:
			print("Exception: MongoDao.MongoDao.insert_tag:",e)
			return []
	
	def find_tag(self, tag):
		try:
			return self.db.tags.find_one({"tag":tag})
		except Exception as e:
			print("Exception: MongoDao.MongoDao.find_tag:",e)
			return []
	
	def add_voted_user(self, room_seq, user_id):
		try:
			return self.db.rooms.update({"room_seq":room_seq},{"$addToSet":{"voted_members":user_id}})
		except Exception as e:
			print("Exception: MongoDao.MongoDao.add_voted_user:",e)
			return []

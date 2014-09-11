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
			return Mongo_Wisewolf.rooms.find({"room_title":{"$regex":"(?i).*"+re_escape(keyword)+".*"}}).sort("_id",-1).skip(req_seq).limit(20)
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
		except:
			print("Exception: MongoDao.MongoDao.find_room:",e)
			return []
	
	def find_chat(self, room_seq, projection= None):
		try:
			return self.db.chat_log.find_one({"room_seq":room_seq}, projection)
		except:
			print("Exception: MongoDao.MongoDao.find_chat:",e)
			return []
	
	def insert_chat(self, room_seq, chat_log):
		try:
			return self.db.chat_log.insert({"room_seq":room_seq, "chat_log":chat_log})
		except:
			print("Exception: MongoDao.MongoDao.insert_chat:",e)
			return []

	def add_chat(self, room_seq, message):
		try:
			return self.db.chat_log.update({"room_seq":room_seq},{"$addToSet":{"chat_log":message}})
		except:
			print("Exception: MongoDao.MongoDao.add_chat:",e)
			return []


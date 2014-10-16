from wisewolf.db_pool import redis_RoomSession, Mongo_Wisewolf
from wisewolf.common.MongoDao import MongoDao
import time

MongoDao= MongoDao()
class RoomValidator:
	def __init__(self, MongoDao= MongoDao):
		self.MongoDao= MongoDao

	def validate_room(self, room_seq, redis_conn= redis_RoomSession, room_collection= Mongo_Wisewolf.rooms):
		try:
			return {"invalid_room":self.is_valid(room_seq, redis_conn, room_collection), "outdated":self.is_outdated(room_seq, redis_conn, room_collection)}
		except Exception as e:
			print("Exception: RoomValidator.RoomValidator.valid_room error:", e)
			return {}
	
	def is_valid(self, room_seq, redis_conn= redis_RoomSession, room_collection= Mongo_Wisewolf.rooms):
		try:
			if self.MongoDao.find_room(room_seq, {"_id":1}) is not None:
				return False
		except Exception as e:
			print("Exception: RoomValidator.RoomValidator.is_valid error:",e)
			return False
		return True
	
		
	def is_outdated(self, room_seq, redis_conn= redis_RoomSession, room_collection= Mongo_Wisewolf.rooms):
		try:
			open_time= float(self.MongoDao.find_room(room_seq,{"open_time":1})["open_time"])
		except Exception as e:
			print("Exception: RoomValidator.RoomValidator.is_outdated error:",e)
			return True
		if time.time()- open_time> 86400:#if passed over 24 hours
			return True
		return False

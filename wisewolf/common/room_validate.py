from wisewolf.db_pool import redis_RoomSession, Mongo_Wisewolf

class room_validator:
	def __init__(self):
		pass
	def validate_room(self, room_seq, redis_conn= redis_RoomSession, room_collection= Mongo_Wisewolf.rooms):
		try:
			return {"invalid_room":self.is_valid(room_seq, redis_conn, room_collection), "outdated":self.is_outdated(room_seq, redis_conn, room_collection)}
		except Exception as e:
			print("Exception: room_validate.room_validator.validate_room error:", e)
			return {}
	
	def is_valid(self, room_seq, redis_conn= redis_RoomSession, room_collection= Mongo_Wisewolf.rooms):
		if room_collection.find_one({"room_seq":room_seq}, {"_id":1}) is not None:
			return False
		return True
	
		
	def is_outdated(self, room_seq, redis_conn= redis_RoomSession, room_collection= Mongo_Wisewolf.rooms):
		if redis_conn.get(room_seq) is None and room_collection.find_one({"room_seq":room_seq},{"_id":1}) is not None:
			return True
		return False

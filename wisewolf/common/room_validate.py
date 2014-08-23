from wisewolf.db_pool import redis_RoomSession, Mongo_Wisewolf

def validate_room(room_seq, redis_conn= redis_RoomSession, room_collection= Mongo_Wisewolf.rooms):
	try:
		return {"invalid_room":is_valid(room_seq, redis_conn, room_collection), "outdated":is_outdated(room_seq, redis_conn, room_collection)}
	except Exception as e:
		print(e)
		return {}

def is_valid(room_seq, redis_conn= redis_RoomSession, room_collection= Mongo_Wisewolf.rooms):
	if room_collection.find_one({"room_seq":room_seq}, {"_id":1}) is not None:
		return False
	return True

	
def is_outdated(room_seq, redis_conn= redis_RoomSession, room_collection= Mongo_Wisewolf.rooms):
	if redis_conn.get(room_seq) is None and room_collection.find_one({"room_seq":room_seq},{"_id":1}) is not None:
		return True
	return False

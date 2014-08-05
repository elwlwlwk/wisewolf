from wisewolf.websocket.chatting.Room import Room
from wisewolf.db_pool import redis_RoomSession, Mongo_Wisewolf

class ChattingRoomSession:
	def __init__(self, session= redis_RoomSession, room_collection= Mongo_Wisewolf.rooms, chat_log_collection= Mongo_Wisewolf.chat_log):
		self.rooms=dict()
		self.redis_conn= session
		self.room_collection= room_collection
		self.chat_log_collection= chat_log_collection

	def add_room(self, room_seq, room_kind="default", session=redis_RoomSession, ):
		if room_seq in self.rooms:
			return
		self.rooms[room_seq]= Room(room_seq, self.redis_conn, self.room_collection, self.chat_log_collection )
			
	def validate_room(self, req_room):
		#prefix= "chat_room:"
		r= self.redis_conn
		val= r.get(req_room)

		if val is None:
			room= Mongo_Wisewolf.rooms.find_one({"room_seq":req_room},{"_id":1})
			if room is None:
				return False
			Mongo_Wisewolf.rooms.update({"room_seq":req_room},{"$set":{"out_dated":True}})
			try:
				self.rooms[req_room].room_meta["out_dated"]= True
			except Exception as e:
				pass
			return True
		else:
			return True
	
	def get_room(self, room_seq):
		return self.rooms[room_seq]


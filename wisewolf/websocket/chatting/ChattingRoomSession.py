from wisewolf.websocket.chatting.Room import Room
from wisewolf.db_pool import redis_RoomSession, Mongo_Wisewolf
from wisewolf.common import Room_Validator

class ChattingRoomSession:
	def __init__(self, session= redis_RoomSession, room_collection= Mongo_Wisewolf.rooms, chat_log_collection= Mongo_Wisewolf.chat_log):
		self.rooms=dict()
		self.redis_conn= session
		self.room_collection= room_collection
		self.chat_log_collection= chat_log_collection

	def add_room(self, room_seq, room_kind="default", session=redis_RoomSession, ):
		if room_seq in self.rooms:
			return False
		self.rooms[room_seq]= Room(room_seq, self.redis_conn, self.room_collection, self.chat_log_collection )
		return True
			
	def validate_room(self, room_seq):
		room_status= Room_Validator.validate_room(room_seq, self.redis_conn, self.room_collection)
		try:
			if room_status["invalid_room"] is True:
				raise Exception("accessing invalid_room")
			elif room_status["outdated"] is True:
				self.outdate_room(room_seq)
		except Exception as e:
			print("Exception: ChattingRoomSession.ChattingRoomSession.validate_room:",e)
			return False
		return True

	def get_room(self, room_seq):
		return self.rooms[room_seq]

	def outdate_room(self, room_seq):
		Mongo_Wisewolf.rooms.update({"room_seq":room_seq},{"$set":{"out_dated":True}})
		try:#error may raise when ChattingRoomSession.rooms has no room_seq as key.
			self.rooms[room_seq].outdate()
		except KeyError as e:
			pass

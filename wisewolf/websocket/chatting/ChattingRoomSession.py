from wisewolf.websocket.chatting.Room import Room
from wisewolf.websocket.chatting import redis_RoomSession

class ChattingRoomSession:
	def __init__(self, session= redis_RoomSession):
		self.rooms=dict()
		self.redis_conn= session

	def add_room(self, room_seq, room_kind="default"):
		if self.rooms.has_key(room_seq):
			return
		self.rooms[room_seq]= Room(room_seq, session= self.redis_conn)
			
	def validate_room(self, req_room, prefix):
		#prefix= "chat_room:"
		r= self.redis_conn
		val= r.get(prefix+req_room)
		if val is None:
			return False
		else:
			return True
	
	def get_room(self, room_seq):
		return self.rooms[room_seq]


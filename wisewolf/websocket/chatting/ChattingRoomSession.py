from wisewolf.websocket.chatting.Room import Room
from wisewolf.websocket.chatting import redis_RoomSession

class ChattingRoomSession:
	def __init__(self):
		self.rooms=dict()

	def add_room(self, room_seq):
		if self.rooms.has_key(room_seq):
			return
		self.rooms[room_seq]= Room(room_seq)
			
	def add_user_to_room(self, chatter, room_seq):
		self.rooms[room_seq].add_chatter(chatter)
	
	def validate_room(self, req_room):
		prefix= "chat_room:"
		r= redis_RoomSession
		val= r.get(prefix+req_room)
		if val is None:
			return False
		else:
			return True
	
	def get_room(self, room_seq):
		return self.rooms[room_seq]

import tornado.websocket
import os
import binascii
from wisewolf.websocket.chatting.ChattingRoomSession import ChattingRoomSession

chatting_room_session= ChattingRoomSession()

class ChattingHandler(tornado.websocket.WebSocketHandler):
	def __init__(self, request, spec_kwargs):
		self.alive= 0
		self.name= binascii.b2a_hex(os.urandom(2))
		self.my_room= None
		tornado.websocket.WebSocketHandler.__init__(self, request, spec_kwargs)
		pass
	def open(self):
		print "new connections!"
		req_room= self.request.uri.split("/")[3]
		print self.request.uri
		if chatting_room_session.validate_room(req_room, "chat_room:"):
			chatting_room_session.add_room(req_room)

			chatting_room_session.rooms[req_room].add_waiting_chatter(self)
			
		else:
			print "invalid access"
			self.close()

	def on_message(self, message):
		self.my_room.message_handler(self, message)

	def on_close(self):
		self.my_room.remove_chatter(self)
	
	def set_my_room(self, room_seq):
		self.my_room= room_seq
	
	def get_name(self):
		return self.name

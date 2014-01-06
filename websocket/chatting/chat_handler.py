import tornado.websocket
import os
import binascii
from websocket.chatting.ChattingRoomSession import ChattingRoomSession

chatting_room_session= ChattingRoomSession()

class ChattingHandler(tornado.websocket.WebSocketHandler):
	def __init__(self, request, spec_kwargs):
		self.alive= 0
		self.name= binascii.b2a_hex(os.urandom(2))
		self.my_room= None
		tornado.websocket.WebSocketHandler.__init__(self, request, spec_kwargs)
		pass
	def open(self):
		req_room= self.request.uri.split("/")[3]
		if chatting_room_session.validate_room(req_room)== True:
			chatting_room_session.add_room(req_room)
			chatting_room_session.add_user_to_room(self, req_room)
			self.my_room.broadcast_room_stat()
			self.my_room.send_cur_chat_log(self)

		else:
			print "invalid access"
			self.close()

	def on_message(self, message):
		self.my_room.message_handler(self, message)

	def on_close(self):
		print "on_close"
		self.my_room.remove_chatter(self)
		self.my_room.broadcast_room_stat()
	
	def set_my_room(self, room_seq):
		self.my_room= room_seq
	
	def get_name(self):
		return self.name

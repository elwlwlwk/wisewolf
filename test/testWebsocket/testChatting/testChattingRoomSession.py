import unittest
from wisewolf.websocket.chatting.ChattingRoomSession import ChattingRoomSession

from wisewolf.websocket.chatting import redis_RoomSession

class TestChattingRoomSession(unittest.TestCase):

	class mock_redisSession():
		def __init__(self):
			self.name=''
			self.value=''

		def get(self, name):
			if self.name != name:
				return None
			else:
				return self.value

		def set(self, name, value):
			self.name= name
			self.value= value

	def setUp(self):
		self.redis_conn= self.mock_redisSession()
		self.session= ChattingRoomSession(session= self.redis_conn)
	
	def test_validate_room(self):
		self.assertFalse(self.session.validate_room("not_valid_room"))
		
		self.redis_conn.set("chat_room:valid_room_for_test", '')
		self.assertTrue(self.session.validate_room("valid_room_for_test"))
	
	def test_add_room(self):
		self.session.add_room("test_room")
		self.assertTrue(self.session.rooms.has_key("test_room"))
		self.assertEquals(self.session.rooms["test_room"].__class__.__name__, "Room")

import unittest
import json
from wisewolf.websocket.chatting.ChattingRoomSession import ChattingRoomSession

from wisewolf.db_pool import redis_RoomSession

class TestChattingRoomSession(unittest.TestCase):
	class mock_redisSession():
		def __init__(self, name="test_room", value=json.dumps({'room_title':'test_room','open_time':'1403913777','room_kind':'generic', 'max_participants':'3'})):
			self.name=name
			self.value=value

		def get(self, name):
			if self.name != name:
				return None
			else:
				return self.value.encode()

		def set(self, name, value):
			self.name= name
			self.value= value

	def setUp(self):
		self.redis_conn= self.mock_redisSession()
		self.session= ChattingRoomSession(session= self.redis_conn)
	
	def test_validate_room(self):
		self.assertFalse(self.session.validate_room("not_valid_room"))
		
		self.redis_conn.set("valid_room_for_test", '')
		self.assertTrue(self.session.validate_room("valid_room_for_test"))
	
	def test_add_room(self):
		self.session.add_room("test_room")
		self.assertTrue("test_room" in self.session.rooms)
		self.assertEqual(self.session.rooms["test_room"].__class__.__name__, "Room")

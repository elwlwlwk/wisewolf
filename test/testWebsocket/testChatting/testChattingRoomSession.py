import unittest
import json
from wisewolf.websocket.chatting.ChattingRoomSession import ChattingRoomSession

from wisewolf.db_pool import redis_RoomSession
from pymongo import MongoClient

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

		client= MongoClient()
		db= client.test_wisewolf
		db.authenticate("test_wisewolf","test_wisewolf")
		self.room_collection= db.rooms
		self.chat_log_collection= db.chat_log

		room_data={"room_seq":"test_room", "room_title":"test_room", "room_kind":"generic","open_time":"1403913777","max_participants":3}
		self.room_collection.insert(room_data)

		self.session= ChattingRoomSession(self.redis_conn, self.room_collection, self.chat_log_collection)

	def tearDown(self):
		self.room_collection.drop()
		self.chat_log_collection.drop()

	def test_validate_room(self):
		self.assertFalse(self.session.validate_room("not_valid_room"))
		
		self.redis_conn.set("valid_room_for_test", '')
		self.assertTrue(self.session.validate_room("valid_room_for_test"))
	
	def test_add_room(self):
		self.session.add_room("test_room","generic")
		self.assertTrue("test_room" in self.session.rooms)
		self.assertEqual(self.session.rooms["test_room"].__class__.__name__, "Room")

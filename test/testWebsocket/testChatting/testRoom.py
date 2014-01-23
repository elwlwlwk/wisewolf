import unittest
import json
from pymongo import MongoClient
from wisewolf.websocket.chatting.Room import Room
from wisewolf.websocket.chatting.chat_handler import ChattingHandler
class TestRoom(unittest.TestCase):
	class mock_chatter():
		def __init__(self):
			self.message=''
			self.alive= 0
			self.status='connect'
			self.name="mock_chatter"
			self.ws_connection="dummy"
		def get_name(self):
			return self.name
		def set_my_room(self, room):
			pass
		def write_message(self, message):
			self.message= message
		def close(self):
			self.status='close'

	class mock_redisSession():
		def __init__(self, name="chat_room:test_room", value=""):
			self.name=name
			self.value=value

		def get(self, name):
			if self.name != name:
				return None
			else:
				return self.value

		def set(self, name, value):
			self.name= name
			self.value= value
	
	def setUp(self):
		client= MongoClient()
		db= client.test_wisewolf
		db.authenticate("test_wisewolf","test_wisewolf")
		self.room_collection= db.rooms

		self.redis_conn= self.mock_redisSession()
		self.room= Room("test_room", session= self.redis_conn,\
room_collection= self.room_collection)
	
	def test_add_chatter(self):
		self.room.add_chatter(self.mock_chatter())
		self.assertTrue("mock_chatter" in self.room.chatters_name)
		self.assertEquals(len(self.room.chatters), 1)
		
		self.room.add_chatter(self.mock_chatter())
		self.assertEquals(len(self.room.chatters), 2)
		self.assertEquals(len(self.room.chatters_name), 2)

	def test_heartbeat_handler(self):
		chatter= self.mock_chatter()
		chatter.alive= -1
		message={"proto_type":"heartbeat","heartbeat_key":"fake_key"}
		self.room.heartbeat_handler(chatter, message)
		self.assertEqual(chatter.alive, -1)
		
		message={"proto_type":"heartbeat","heartbeat_key":self.room.heartbeat_key}
		self.room.heartbeat_handler(chatter, message)
		self.assertEqual(chatter.alive, 0)

	def test_send_heartbeat(self):
		chatter= self.mock_chatter()
		chatter2= self.mock_chatter()
		self.room.add_chatter(chatter)
		self.room.add_chatter(chatter2)

		self.room.heartbeat_time= 0
		self.room.send_heartbeat()
		self.assertEqual(chatter.alive, -1)
		self.assertEqual(chatter2.alive, -1)

		self.room.heartbeat_time= 0
		self.room.send_heartbeat()
		self.assertEqual(chatter.alive, -2)
		self.assertEqual(chatter2.alive, -2)

		message={"proto_type":"heartbeat","heartbeat_key":self.room.heartbeat_key}
		self.room.heartbeat_time= 0
		self.room.heartbeat_handler(chatter, message)
		self.room.send_heartbeat()
		self.assertEqual(chatter.status, "connect")
		self.assertEqual(chatter2.status, "close")
	
	def test_write_message(self):
		message={"proto_type":"chat_message","message":"test_message"}
		chatter= self.mock_chatter()
		self.room.write_message(chatter, message)
		self.assertEqual(chatter.message, json.dumps(message))
	
	def test_broadcast(self):
		chatter= self.mock_chatter()
		self.room.add_chatter(chatter)
		message={"proto_type":"chat_message","message":"test_message"}
		self.room.broadcast(message)
		self.assertEquals(chatter.message, json.dumps(message))

		chatter2= self.mock_chatter()
		self.room.add_chatter(chatter2)
		message={"proto_type":"chat_message","message":"test_message2"}
		self.room.broadcast(message)
		self.assertEquals(chatter.message, json.dumps(message))
		self.assertEquals(chatter2.message, json.dumps(message))

	def test_unicast(self):
		chatter= self.mock_chatter()
		self.room.add_chatter(chatter)
		message={"proto_type":"chat_message","message":"test_message"}
		self.room.unicast(chatter, message)
		self.assertEquals(chatter.message, json.dumps(message))
	
		chatter2= self.mock_chatter()
		self.room.add_chatter(chatter2)
		message2={"proto_type":"chat_message","message":"test_message2"}
		self.room.unicast(chatter2, message2)
		message3={"proto_type":"chat_message","message":"test_message2-1"}
		self.room.unicast(chatter, message3)
		self.assertEquals(chatter.message, json.dumps(message3))
		self.assertEquals(chatter2.message, json.dumps(message2))
	
	def test_remove_chatter(self):
		chatter= self.mock_chatter()
		self.room.add_chatter(chatter)
		self.room.remove_chatter(chatter)
		self.assertEquals(len(self.room.chatters), 0)

	def test_assemble_chat(self):
		chatter= self.mock_chatter()
		test_message= self.room.assemble_chat(chatter, {"message":"test_message"})
		dest_message={"proto_type":"chat_message", "sender":chatter.get_name(), "message":"test_message",\
"chat_seq": 0}
		self.assertEquals(test_message, dest_message)

	def test_write_chat_redis(self):
		message={"proto_type":"chat_message","message":"test_message"}
		packed_message=[message]
		self.room.write_chat_redis(message)
		self.assertEqual(self.redis_conn.get("chat_room:test_room"), json.dumps(packed_message))

		message2={"proto_type":"chat_message","message":"test_message2"}
		self.room.write_chat_redis(message2)
		packed_message=[message, message2]
		self.assertEqual(self.redis_conn.get("chat_room:test_room"), json.dumps(packed_message))

	def test_load_chat_redis(self):
		self.assertEqual(self.room.load_chat_redis(), [])
		message={"proto_type":"chat_message","message":"test_message"}
		self.room.write_chat_redis(message)
		self.assertEqual(self.room.load_chat_redis(), [message])
		
	def test_send_cur_chat_log(self):
		chatter= self.mock_chatter()
		self.room.add_chatter(chatter)
		self.assertEqual(self.room.send_cur_chat_log(chatter),None)
		message={"proto_type":"chat_message","message":"test_message"}
		self.room.write_chat_redis(message)
		self.room.send_cur_chat_log(chatter)
		self.assertEqual(chatter.message, json.dumps(message))

	def test_message_handler(self):
		chatter= self.mock_chatter()
		self.room.add_chatter(chatter)
		message={"proto_type":"chat_message","message":"test_message"}
		dest_message={"proto_type":"chat_message", "sender":chatter.get_name(), "message":"test_message",\
"chat_seq": 0}
		self.room.message_handler(chatter, json.dumps(message))
		self.assertEqual(chatter.message, json.dumps(dest_message))
	
	def test_extract_exceed_messages(self):
		messages=[]
		for i in range(50):
			message={"proto_type":"chat_message", "message":"test"+str(i), "chat_seq":i }
			messages.append(message)
		extracted_messages, shrinked_messages= self.room.extract_exceed_messages(messages)
		if len(messages) >= 20:
			self.assertEqual(len(shrinked_messages), 20)
		else:
			self.assertEqual(len(shrinked_messages), len(messages))
		self.assertEqual(len(messages), len(shrinked_messages)+ len(extracted_messages))
	
	def test_write_messages_redis(self):
		messages=[]
		for i in range(50):
			message={"proto_type":"chat_message", "message":"test"+str(i), "chat_seq":i }
			messages.append(message)
		self.room.write_messages_redis(messages)
		self.assertEqual(self.redis_conn.value, json.dumps(messages))
	
	def test_broadcast_room_stat(self):
		chatter= self.mock_chatter()
		chatter2= self.mock_chatter()
		chatter2.name="mock_chatter2"

		self.room.add_chatter(chatter)
		self.room.add_chatter(chatter2)
		self.room.broadcast_room_stat()

		message={"proto_type":"room_stat", "room_seq":self.room.room_seq,\
"chatters":["mock_chatter","mock_chatter2"]}

		self.assertEqual(chatter.message, json.dumps(message))
		self.assertEqual(chatter2.message, json.dumps(message))

	def test_save_chat_mongo(self):
		try:
			messages=[]
			for i in range(50):
				message={"proto_type":"chat_message", "message":"test"+str(i), "chat_seq":i }
				messages.append(message)
			self.room.write_messages_redis(messages)
			self.room.save_chat_mongo()
			msg_to_mongo, msg_to_redis= self.room.extract_exceed_messages(messages)
			self.assertEqual(self.redis_conn.value, json.dumps(msg_to_redis))
			self.assertEqual(self.room_collection.find_one({'room_seq':'test_room'})["chat_log"], msg_to_mongo)
	
			messages2=[]
			for i in range(50, 100):
				message={"proto_type":"chat_message", "message":"test"+str(i), "chat_seq":i }
				messages2.append(message)
			self.room.write_messages_redis(messages2)
			self.room.save_chat_mongo()
			msg_to_mongo, msg_to_redis= self.room.extract_exceed_messages(messages2)
			self.assertEqual(self.redis_conn.value, json.dumps(msg_to_redis))
			self.assertEqual(self.room_collection.find_one({'room_seq':'test_room'})["chat_log"], messages+msg_to_mongo)


		finally:	
			self.room_collection.drop()
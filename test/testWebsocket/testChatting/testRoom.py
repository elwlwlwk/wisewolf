import unittest
import json
from pymongo import MongoClient
from wisewolf.websocket.chatting.Room import Room
from wisewolf.websocket.chatting.chat_handler import ChattingHandler

from test.mock import mock_request, mock_chatter, mock_redisSession

class TestRoom(unittest.TestCase):
	def setUp(self):
		client= MongoClient()
		db= client.test_wisewolf
		db.authenticate("test_wisewolf","test_wisewolf")
		self.room_collection= db.rooms
		self.chat_log_collection= db.chat_log

		room_data={"room_seq":"test_room", "room_title":"test_room", "room_kind":"generic","open_time":"1403913777","max_participants":3,"out_dated":False}
		self.room_collection.insert(room_data)

		self.redis_conn= mock_redisSession()
		self.room= Room("test_room", session= self.redis_conn,\
room_collection= self.room_collection, chat_log_collection= self.chat_log_collection)

	def tearDown(self):
		self.room_collection.drop()
		self.chat_log_collection.drop()

	def test_add_chatter(self):	#testcase for generic room
		mock_chatter= mock_chatter()
		self.room.add_chatter(mock_chatter)
		self.assertTrue(mock_chatter in self.room.chatters)
		self.assertEqual(len(self.room.chatters), 1)
		self.assertEqual(self.room.chatters[0].role, 'opper')
		
		self.room.add_chatter(mock_chatter())
		self.room.add_chatter(mock_chatter())
		self.room.add_chatter(mock_chatter())
		self.assertEqual(len(self.room.chatters), 4)
		self.assertEqual(self.room.chatters[0].role, 'opper')
		self.assertEqual(self.room.chatters[1].role, 'common')
		self.assertEqual(self.room.chatters[2].role, 'observer')
		self.assertEqual(self.room.chatters[3].role, 'observer')
	
	def test_add_chatter(self):	#testcase for versus room
		self.room.room_meta['room_kind']="versus"
		self.room.add_chatter(mock_chatter())
		self.room.add_chatter(mock_chatter())
		self.room.add_chatter(mock_chatter())
		self.assertEqual(self.room.chatters[0].role, 'opper')
		self.assertEqual(self.room.chatters[1].role, 'common')
		self.assertEqual(self.room.chatters[2].role, 'observer')

	def test_add_waiting_chatter(self):
		chatter= mock_chatter()
		self.room.add_waiting_chatter(chatter)
		self.assertTrue(chatter in self.room.waiting_chatters)
	
	def test_first_handshake(self):
		chatter= mock_chatter()
		self.room.add_waiting_chatter(chatter)
		self.assertTrue(chatter in self.room.waiting_chatters)

		self.room.handle_first_handshake(chatter)
		self.assertTrue(chatter not in self.room.waiting_chatters)
		self.assertTrue(chatter in self.room.chatters)

	def test_heartbeat_handler(self):
		chatter= mock_chatter()
		chatter.alive= -1
		message={"proto_type":"heartbeat","heartbeat_key":"fake_key"}
		self.room.heartbeat_handler(chatter, message)
		self.assertEqual(chatter.alive, -1)
		
		message={"proto_type":"heartbeat","heartbeat_key":self.room.heartbeat_key}
		self.room.heartbeat_handler(chatter, message)
		self.assertEqual(chatter.alive, 0)

	def test_send_heartbeat(self):
		chatter= mock_chatter()
		chatter2= mock_chatter()
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
	
	def test_broadcast(self):
		chatter= mock_chatter()
		self.room.add_chatter(chatter)
		message={"proto_type":"chat_message","message":"test_message","chat_seq":0}
		self.room.broadcast(message)
		self.assertEqual(chatter.message, json.dumps(message))

		chatter2= mock_chatter()
		self.room.add_chatter(chatter2)
		message={"proto_type":"chat_message","message":"test_message2","chat_seq":1}
		self.room.broadcast(message)
		self.assertEqual(chatter.message, json.dumps(message))
		self.assertEqual(chatter2.message, json.dumps(message))

	def test_unicast(self):
		chatter= mock_chatter()
		self.room.add_chatter(chatter)
		message={"proto_type":"chat_message","message":"test_message","chat_seq":0}
		self.room.unicast(chatter, message)
		self.assertEqual(chatter.message, json.dumps(message))
	
		chatter2= mock_chatter()
		self.room.add_chatter(chatter2)
		message2={"proto_type":"chat_message","message":"test_message2","chat_seq":2}
		self.room.unicast(chatter2, message2)
		message3={"proto_type":"chat_message","message":"test_message2-1","chat_seq":3}
		self.room.unicast(chatter, message3)
		self.assertEqual(chatter.message, json.dumps(message3))
		self.assertEqual(chatter2.message, json.dumps(message2))
	
	def test_remove_chatter(self):
		chatter= mock_chatter()
		self.room.add_chatter(chatter)
		self.room.remove_chatter(chatter)
		self.assertEqual(len(self.room.chatters), 0)

	def test_assemble_chat(self):
		chatter= mock_chatter()
		test_message= self.room.assemble_chat(chatter, {"message":"test_message"})
		dest_message={"proto_type":"chat_message", "sender":chatter.get_name(), "message":"test_message",\
"chat_seq": 1}
		self.assertEqual(test_message, dest_message)

	def test_send_cur_chat_log(self):
		chatter= mock_chatter()
		self.room.add_chatter(chatter)
		self.assertEqual(self.room.send_cur_chat_log(chatter),None)
		message={"proto_type":"chat_message","message":"test_message","chat_seq":0}
		self.room.save_chat_mongo(message)
		self.room.send_cur_chat_log(chatter)
		self.assertEqual(chatter.message, json.dumps(message))

	def test_message_handler(self):
		chatter= mock_chatter()
		self.room.add_chatter(chatter)
		message={"proto_type":"chat_message","message":"test_message"}
		dest_message={"proto_type":"chat_message", "sender":chatter.get_name(), "message":"test_message",\
"chat_seq": 1}
		self.room.message_handler(chatter, json.dumps(message))
		self.assertEqual(chatter.message, json.dumps(dest_message))
	
	def test_message_handler2(self):
		chatter= mock_chatter()
		self.room.add_chatter(chatter)
		messages=[]
		for i in range(50):
			message={"proto_type":"chat_message", "message":"test"+str(i), "chat_seq":i, "past_chat":"true" }
			messages.append(message)
		for message in messages:
			self.room.save_chat_mongo(message)
		message={"proto_type":"req_past_messages", "last_index":30}
		self.room.message_handler(chatter, json.dumps(message))
		self.assertEqual(chatter.message, json.dumps(messages[28]))
	
	def test_broadcast_chat(self):
		chatter= mock_chatter()
		chatter2= mock_chatter()
		self.room.add_chatter(chatter)
		self.room.add_chatter(chatter2)
		message={"proto_type":"chat_message", "message":"test_message"}
		dest_message={"proto_type":"chat_message", "sender":chatter.get_name(), "message":"test_message",\
"chat_seq": 1}
		self.room.message_handler(chatter, json.dumps(message))
		self.assertEqual(chatter.message, json.dumps(dest_message))
		self.assertEqual(chatter2.message, json.dumps(dest_message))
	
	def test_chat_handler(self):
		chatter= mock_chatter(name='eeee')
		chatter2= mock_chatter()
		self.room.add_chatter(chatter)
		self.room.add_chatter(chatter2)
		self.room.set_role(self.room.chatters[1], 'observer')
		message={"proto_type":"chat_message", "message":"test_message"}
		dest_message={"proto_type":"chat_message", "sender":chatter.get_name(), "message":"test_message",\
"chat_seq": 1}
		self.room.message_handler(chatter, json.dumps(message))
		self.assertEqual(chatter.message, json.dumps(dest_message))
		self.assertEqual(chatter2.message, json.dumps(dest_message))

		self.room.message_handler(chatter2, json.dumps(message))# Don't broadcast message when sender is observer
		self.assertEqual(chatter.message, json.dumps(dest_message))
		self.assertEqual(chatter2.message, json.dumps(dest_message))

	def test_send_past_chats(self):
		chatter= mock_chatter()
		self.room.add_chatter(chatter)
		messages=[]
		for i in range(50):
			message={"proto_type":"chat_message", "message":"test"+str(i), "chat_seq":i, "past_chat":"true" }
			messages.append(message)
		for message in messages:
			self.room.save_chat_mongo(message)
		message={"proto_type":"req_past_messages", "last_index":30}
		self.room.send_past_chats(chatter, 30)
		self.assertEqual(chatter.message, json.dumps(messages[28]))
	
	
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
	
	def test_broadcast_room_stat(self):
		chatter= mock_chatter()
		chatter2= mock_chatter()
		chatter2.name="mock_chatter2"

		self.room.add_chatter(chatter)
		self.room.add_chatter(chatter2)
		self.room.add_chatter(mock_chatter())
		self.room.add_chatter(mock_chatter())
		self.room.broadcast_room_stat()

		message={"proto_type":"room_stat", "room_seq":self.room.room_seq,\
"chatters":["mock_chatter","mock_chatter2", "mock_chatter"]}

		self.assertEqual(chatter.message, json.dumps(message))
		self.assertEqual(chatter2.message, json.dumps(message))

	def test_save_chat_mongo(self):
		messages=[]
		for i in range(50):
			message={"proto_type":"chat_message", "message":"test"+str(i), "chat_seq":i }
			messages.append(message)
		for message in messages:
			self.room.save_chat_mongo(message)
		mongo_room_id= self.room_collection.find_one({'room_seq':self.room.room_seq})["_id"]
		self.assertEqual(self.chat_log_collection.find_one({'room_id':mongo_room_id})["chat_log"], messages)

	def test_get_chat_seq(self):
		self.assertEqual(self.room.get_chat_seq(), 0)
		messages=[]
		for i in range(50):
			message={"proto_type":"chat_message", "message":"test"+str(i), "chat_seq":i }
			messages.append(message)
		for message in messages:
			self.room.save_chat_mongo(message)
		self.assertEqual(self.room.get_chat_seq(), 49)
	
	
	def test_load_chat_mongo(self):
		messages=[]
		for i in range(50):
			message={"proto_type":"chat_message", "message":"test"+str(i), "chat_seq":i }
			messages.append(message)
		for message in messages:
			self.room.save_chat_mongo(message)

		self.assertEqual(self.room.load_chat_mongo(30,threshold=20), messages[9:29])
	
	def test_set_role(self):
		chatter=mock_chatter()
		self.room.add_chatter(chatter)
		self.room.set_role(self.room.chatters[0], "opper")
		self.assertEqual(self.room.chatters[0].role, "opper")
	

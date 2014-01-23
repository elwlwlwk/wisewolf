import json
import binascii

from time import time
from os import urandom
from flask import Markup
from types import *
from operator import itemgetter

from wisewolf.websocket.chatting import redis_RoomSession

from pymongo import MongoClient

class Room:
	def __init__(self, room_seq, session=redis_RoomSession, room_collection= None):
		self.chat_seq= 0
		self.room_seq= room_seq
		self.chatters=[]
		self.chatters_name=[]
		self.redis_conn= session
		db= MongoClient().wisewolf
		db.authenticate("wisewolf","dlalsrb3!")
		room_collection= db.rooms
		self.room_collection= room_collection
		self.prefix="chat_room:"
		self.heartbeat_time= int(time())
		self.heartbeat_key= urandom(12)

	def add_chatter(self, chatter):
		self.chatters.append(chatter)
		self.chatters_name.append(chatter.get_name())
		chatter.set_my_room(self)

	def send_heartbeat(self):
		cur_time= int(time())
		if cur_time- self.heartbeat_time >= 5:
			self.heartbeat_key= binascii.b2a_hex(urandom(12))
			heartbeat_msg={}
			heartbeat_msg["proto_type"]= "heartbeat"
			heartbeat_msg["heartbeat_key"]= self.heartbeat_key
			for chatter in self.chatters:
				if chatter.alive== -2:
					self.remove_chatter(chatter)
					chatter.close()
				else:
					chatter.alive-= 1
					self.write_message(chatter, heartbeat_msg)
			self.heartbeat_time= cur_time

	def heartbeat_handler(self, chatter, message):
		if message["heartbeat_key"]== self.heartbeat_key:
			chatter.alive= 0
	
	def write_message(self, chatter, message):
		if message["proto_type"]!= "heartbeat":
			self.send_heartbeat()
		if type(chatter.ws_connection) is not NoneType:
			if message["proto_type"]== "chat_message":
				if message["chat_seq"] != 0 and message["chat_seq"] % 40 is 0:
					self.save_chat_mongo()
			chatter.write_message(json.dumps(message))

	def broadcast(self, message):
		for chatter in self.chatters:
			self.write_message(chatter, message)
	
	def unicast(self, chatter, message):
		if chatter in self.chatters:
			self.write_message(chatter, message)

	def remove_chatter(self, chatter):
		self.chatters.remove(chatter)
		self.chatters_name.remove(chatter.get_name())
		self.broadcast_room_stat()
	
	def assemble_chat(self, chatter, message):
		chat_message={}
		chat_message["proto_type"]= "chat_message"
		chat_message["sender"]= chatter.get_name()
		chat_message["message"]= Markup.escape(message["message"])
		chat_message["chat_seq"]= self.chat_seq
		self.chat_seq+= 1
		return chat_message

	def write_chat_redis(self, chat_message):
		chat_log=[chat_message]
		self.write_messages_redis(chat_log)

	def broadcast_chat(self, chatter, message):
		chat_message= self.assemble_chat(chatter, message)
		self.write_chat_redis(chat_message)
		self.broadcast(chat_message)
		
	def broadcast_room_stat(self):
		room_stat={}
		room_stat["proto_type"]="room_stat"
		room_stat["room_seq"]= self.room_seq
		room_stat["chatters"]= self.chatters_name
		self.broadcast(room_stat)
	
	def load_chat_redis(self):
		loaded_data= self.redis_conn.get(self.prefix+ self.room_seq)
		loaded_messages=[]
		if loaded_data != '':
			messages= json.loads(loaded_data)
			for message in messages:
				loaded_messages.append(message)
		return loaded_messages

	def send_cur_chat_log(self, chatter):
		chat_log= self.load_chat_redis()
		if chat_log!= '':
			for chat in chat_log:
				self.unicast(chatter, chat)
		
	def message_handler(self, chatter, message):
		loaded_msg= json.loads(message)
		if loaded_msg["proto_type"]== "chat_message":
			self.broadcast_chat(chatter, loaded_msg)
		elif loaded_msg["proto_type"]== "heartbeat":
			self.heartbeat_handler(chatter, loaded_msg)

	def extract_exceed_messages(self, messages, threshold= 20):
		loaded_messages=[]
		for message in messages:
			loaded_messages.append(message)
			loaded_messages= sorted(loaded_messages, key=itemgetter("chat_seq"))

		if len(messages)> threshold:
			return loaded_messages[0: len(messages)-threshold], loaded_messages[len(messages)-threshold:]
		else:
			return [],loaded_messages
	
	def write_messages_redis(self, messages, append= True):
		if append is True:
			chat_log= self.load_chat_redis()+ messages
		else:
			chat_log= messages
		self.redis_conn.set(self.prefix+ self.room_seq, json.dumps(chat_log))

	def save_chat_mongo(self, threshold= 20):
		msg_to_mongo, msg_to_redis= self.extract_exceed_messages(self.load_chat_redis(), threshold= threshold)
		self.write_messages_redis(msg_to_redis, append= False)
		room_document= self.room_collection.find_one({"room_seq":self.room_seq})
		if room_document is None:
			room_data={"room_seq":self.room_seq,"chat_log":msg_to_mongo}
			self.room_collection.insert(room_data)
		else:
			self.room_collection.update({"room_seq":self.room_seq},{"$set":{"chat_log":room_document["chat_log"]+msg_to_mongo}})

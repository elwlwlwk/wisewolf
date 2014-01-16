import json
import binascii

from time import time
from os import urandom
from flask import Markup
from types import *

from wisewolf.websocket.chatting import redis_RoomSession

class Room:
	def __init__(self, room_seq, session=redis_RoomSession):
		self.chat_seq= 0
		self.room_seq= room_seq
		self.chatters=[]
		self.chatters_name=[]
		self.redis_conn= session
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
					self.broadcast_room_stat()
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
		if type(chatter) is not None:
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
	
	def assemble_chat(self, chatter, message):
		chat_message={}
		chat_message["proto_type"]= "chat_message"
		chat_message["sender"]= chatter.get_name()
		chat_message["message"]= Markup.escape(message["message"])
		chat_message["chat_seq"]= self.chat_seq
		self.chat_seq+= 1
		return chat_message

	def write_chat_redis(self, chat_message):
		chat_log=[]
		loaded_data= self.redis_conn.get(self.prefix+ self.room_seq)
		if loaded_data != '':
			chat_log= json.loads(loaded_data)			
		chat_log.append(json.dumps(chat_message))
		self.redis_conn.set(self.prefix+ self.room_seq, json.dumps(chat_log))

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
	
	def write_chat_redis(self, chat_message):
		chat_log=[]
		loaded_data= self.redis_conn.get(self.prefix+ self.room_seq)
		if loaded_data != '':
			chat_log= json.loads(loaded_data)			
		chat_log.append(json.dumps(chat_message))
		self.redis_conn.set(self.prefix+ self.room_seq, json.dumps(chat_log))

	def load_chat_redis(self):
		loaded_data= self.redis_conn.get(self.prefix+ self.room_seq)
		if loaded_data != '':
			return json.loads(loaded_data)
		return ''

	def send_cur_chat_log(self, chatter):
		chat_log= self.load_chat_redis()
		if chat_log!= '':
			for chat in chat_log:
				self.unicast(chatter, json.loads(chat))
		
	def message_handler(self, chatter, message):
		loaded_msg= json.loads(message)
		if loaded_msg["proto_type"]== "chat_message":
			self.broadcast_chat(chatter, loaded_msg)
		elif loaded_msg["proto_type"]== "heartbeat":
			self.heartbeat_handler(chatter, loaded_msg)

	def save_chat_mongo(self):
		pass

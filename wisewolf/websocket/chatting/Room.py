import json
import binascii

import pickle
from time import time
from os import urandom
from flask import Markup
from types import *
from operator import itemgetter

from wisewolf.db_pool import Mongo_Wisewolf, redis_RoomSession, redis_UserSession
from wisewolf.common import MongoDao

class Room:
	def __init__(self, room_seq, session=redis_RoomSession, room_collection= None, chat_log_collection= None, MongoDao= MongoDao):
		self.room_seq= room_seq
		self.chatters=[]
		self.redis_conn= session
		db=Mongo_Wisewolf
		self.MongoDao=MongoDao

		if chat_log_collection is None:
			self.chat_log_collection= db.chat_log
		else:
			self.chat_log_collection= chat_log_collection

		self.heartbeat_time= int(time())
		self.heartbeat_key= urandom(12)
		self.chat_seq= self.get_chat_seq()+1

		self.room_meta= self.MongoDao.find_room(self.room_seq)
	
	def outdate(self):
		self.room_meta["out_dated"]= True

	def add_chatter(self, chatter):
		chatter.set_my_room(self)
		try:
			if self.room_meta["max_participants"]!= ''and len(self.chatters)>= int(self.room_meta["max_participants"]):
				chatter.role="observer"
			if self.room_meta["out_dated"]== True:
				chatter.role="observer"
		except ValueError as e:
			print("ValueError: Room.Room.add_chatter:",e)
			self.room_meta["max_participants"]=''
		if len(self.chatters) is 0:
			chatter.role="opper"
		if self.room_meta["room_kind"]=="versus" and len(self.chatters) is 1:
			chatter.role="common"
		elif self.room_meta["room_kind"]=="versus" and len(self.chatters) > 1:
			chatter.role="observer"
		self.chatters.append(chatter)
		self.broadcast_room_stat()
		self.send_cur_chat_log(chatter)

	def update_redis(self):
		pass

	def send_heartbeat(self):
		cur_time= int(time())
		if cur_time- self.heartbeat_time >= 5:
			self.heartbeat_key= binascii.b2a_hex(urandom(12)).decode("utf-8")
			heartbeat_msg={}
			heartbeat_msg["proto_type"]= "heartbeat"
			heartbeat_msg["heartbeat_key"]= self.heartbeat_key
			for chatter in self.chatters:
				if chatter.alive== -2:
					#print("[timeout] "+chatter.request.headers["X-Real-Ip"]+" "+chatter.name)
					self.remove_chatter(chatter)
					chatter.close()
				else:
					chatter.alive-= 1
					self.unicast(chatter, heartbeat_msg)
			self.heartbeat_time= cur_time

	def heartbeat_handler(self, chatter, message):
		if message["heartbeat_key"]== self.heartbeat_key:
			chatter.alive= 0
	
	def unicast(self, chatter, message):
		if message["proto_type"]!= "heartbeat":
			self.send_heartbeat()
		if type(chatter.ws_connection) is not None:
			chatter.write_message(json.dumps(message))

	def broadcast(self, message):
		for chatter in self.chatters:
			self.unicast(chatter, message)
	
	def remove_chatter(self, chatter):
		self.chatters.remove(chatter)
		self.broadcast_room_stat()
	
	def assemble_chat(self, chatter, message):
		chat_message={}
		chat_message["proto_type"]= "chat_message"
		chat_message["sender"]= chatter.get_name()
		chat_message["message"]= Markup.escape(message["message"]).replace("\n","<br />")
		chat_message["chat_seq"]= self.chat_seq
		self.chat_seq+= 1
		return chat_message

	def broadcast_chat(self, chatter, message):
		chat_message= self.assemble_chat(chatter, message)
		self.save_chat_mongo(chat_message)
		self.broadcast(chat_message)
		
	def broadcast_room_stat(self):
		room_stat={}
		chatters_name=[]
		for chatter in self.chatters:
			if chatter.role!= "observer":
				chatters_name.append(chatter.name)
		room_stat["proto_type"]="room_stat"
		room_stat["room_seq"]= self.room_seq
		room_stat["chatters"]= chatters_name
		self.broadcast(room_stat)
	
	def send_cur_chat_log(self, chatter):
		chat_log= self.load_chat_mongo(last_chat= True, threshold=40)
		if chat_log!= '':
			for chat in chat_log:
				self.unicast(chatter, chat)
		
	def message_handler(self, chatter, message):
		loaded_msg= json.loads(message)
		if loaded_msg["proto_type"]== "chat_message":
			self.chat_handler(chatter, loaded_msg)
		elif loaded_msg["proto_type"]== "heartbeat":
			self.heartbeat_handler(chatter, loaded_msg)
		elif loaded_msg["proto_type"]== "req_past_messages":
			self.send_past_chats(chatter, loaded_msg["last_index"])
		elif loaded_msg["proto_type"]=="first_handshake":			
			self.handle_first_handshake(chatter, loaded_msg["user_id"])
	
	def chat_handler(self, chatter, message):
		if chatter.role in ['observer'] or self.room_meta["out_dated"]== True:
			return
		self.broadcast_chat(chatter, message)
	
	def handle_first_handshake(self, chatter, user_id=""):
		if chatter in self.chatters:
			self.chatters.remove(chatter)
			redis= redis_UserSession
			val = redis.get("session:"+ user_id)
			if val is not None:
				val = pickle.loads(val)
				chatter.name= val['user']
			self.add_chatter(chatter)
		else:
			return
	
	def set_role(self, chatter, role='common'):
		chatter.role= role
	
	def send_past_chats(self, chatter, last_index):
		past_chats= self.load_chat_mongo(last_index)
		for chat in past_chats:
			chat["past_chat"]="true";
			self.unicast(chatter, chat)

	def extract_exceed_messages(self, messages, threshold= 20):
		loaded_messages=[]
		for message in messages:
			loaded_messages.append(message)
			loaded_messages= sorted(loaded_messages, key=itemgetter("chat_seq"))

		if len(messages)> threshold:
			return loaded_messages[0: len(messages)-threshold], loaded_messages[len(messages)-threshold:]
		else:
			return [],loaded_messages
	
	def save_chat_mongo(self, message, append= True):
		if append is True:
			room_document= self.MongoDao.find_room(self.room_seq, {"room_seq":1})
			chat_log_document= self.MongoDao.find_chat(self.room_seq, {"_id":1})
			if chat_log_document is None:
				self.MongoDao.insert_chat(room_document["room_seq"],[message])
			else:
				self.MongoDao.add_chat(room_document["room_seq"], message)
		else:
			pass
	
	def get_chat_seq(self):
		chat_log= self.load_chat_mongo(last_chat= True)
		if len(chat_log) is 0:
			return 0
		else:
			chat_log= sorted(chat_log, key=itemgetter("chat_seq"))
			return chat_log[len(chat_log)-1]["chat_seq"]
	
	def load_chat_mongo(self, last_index=0, threshold=20, last_chat= False):
		room_document= self.MongoDao.find_room(self.room_seq, {"room_seq":1})
		if room_document is None:
			return []
		else:
			mongo_room_seq= room_document["room_seq"]
			chat_log_document= self.MongoDao.find_chat(mongo_room_seq, {"_id":1})
			if chat_log_document is None:
				return []
			if last_chat is True:
				return self.MongoDao.find_chat(mongo_room_seq, {"chat_log":{"$slice":threshold*-1}})["chat_log"]
			else:
				if last_index-threshold < 0:
					return self.MongoDao.find_chat(mongo_room_seq,{"chat_log":{"$slice":[0, last_index-1]}})["chat_log"]
				return self.MongoDao.find_chat(mongo_room_seq,{"chat_log":{"$slice":[last_index-threshold-1, threshold]}})["chat_log"]

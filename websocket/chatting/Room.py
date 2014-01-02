import json
from redis import Redis

class Room:
	def __init__(self, room_seq):
		self.room_seq= room_seq
		self.chatters=[]
		self.chatter_names=[]
		self.redis_conn= Redis(db=1)		
		self.prefix="chat_room:"

	def add_chatter(self, chatter):
		self.chatters.append(chatter)
		self.chatter_names.append(chatter.get_name())
		chatter.set_my_room(self)
		
	def broadcast(self, message):
		for chatter in self.chatters:
			chatter.write_message(message)
	
	def unicast(self, chatter, message):
		if chatter in self.chatters:
			chatter.write_message(message)

	def remove_chatter(self, chatter):
		self.chatters.remove(chatter)
		self.chatter_names.remove(chatter.get_name())

	def broadcast_chat(self, chatter, message):
		chat_message={}
		chat_message["proto_type"]= "chat_message"
		chat_message["sender"]= chatter.get_name()
		chat_message["message"]= message
		self.write_chat_redis(chat_message)
		self.broadcast(json.dumps(chat_message))
		
	def broadcast_room_stat(self):
		room_stat={}
		room_stat["proto_type"]="room_stat"
		room_stat["room_seq"]= self.room_seq
		room_stat["chatters"]= self.chatter_names
		self.broadcast(json.dumps(room_stat))
	
	def write_chat_redis(self, chat_message):
		import json
		chat_log=[]
		loaded_data= self.redis_conn.get(self.prefix+ self.room_seq)
		if loaded_data != '':
			chat_log= json.loads(loaded_data)			
		chat_log.append(json.dumps(chat_message))
		self.redis_conn.set(self.prefix+ self.room_seq, json.dumps(chat_log))

	def send_cur_chat_log(self, chatter):
		chat_log= self.load_chat_redis()
		for chat in chat_log:
			self.unicast(chatter, chat)
		
	def load_chat_redis(self):
		import json
		loaded_data= self.redis_conn.get(self.prefix+ self.room_seq)
		if loaded_data != '':
			return json.loads(loaded_data)
		return ''

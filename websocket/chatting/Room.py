import json
from redis import Redis

class Room:
	def __init__(self, room_seq):
		self.room_seq= room_seq
		self.chatters=[]
		self.chatter_names=[]
		self.redis_conn= Redis(db=1)		

	def add_chatter(self, chatter):
		self.chatters.append(chatter)
		self.chatter_names.append(chatter.get_name())
		chatter.set_my_room(self)
		
	def send_to_all(self, message):
		for chatter in self.chatters:
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
		self.send_to_all(json.dumps(chat_message))
		
	def broadcast_room_stat(self):
		room_stat={}
		room_stat["proto_type"]="room_stat"
		room_stat["room_seq"]= self.room_seq
		room_stat["chatters"]= self.chatter_names
		self.send_to_all(json.dumps(room_stat))
	
	def write_chat_redis(self, chat_message):
		import json
		prefix="chat_room:"
		chat_log=[]
		loaded_data= self.redis_conn.get(prefix+ self.room_seq)
		if loaded_data != '':
			chat_log= json.loads(loaded_data)			
		chat_log.append(json.dumps(chat_message))
		self.redis_conn.set(prefix+ self.room_seq, json.dumps(chat_log))

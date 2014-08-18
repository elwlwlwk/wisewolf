import json

class mock_request():
	def __init__(self):
		self.headers={"X-Real-Ip":"127.0.0.1"}

class mock_chatter():
	def __init__(self, name="mock_chatter"):
		self.message=''
		self.alive= 0
		self.status='connect'
		self.name= name
		self.ws_connection="dummy"
		self.role= 'common'
		self.request= mock_request()
	def get_name(self):
		return self.name
	def set_my_room(self, room):
		pass
	def write_message(self, message):
		self.message= message
	def close(self):
		self.status='close'

class mock_redisSession():
	def __init__(self, name="test_room", value=json.dumps({'room_title':'test_room','open_time':'1403913777','room_kind':'generic', 'max_participants':'3'})):
		self.name=name
		self.value=value

	def get(self, name):
		if self.name!= name:
			return None
		else:
			return self.value.encode()

	def set(self, name, value):
		self.name= name
		self.value= value

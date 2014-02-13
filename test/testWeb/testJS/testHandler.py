import tornado.websocket
import os
import binascii

import json
class testHandler(tornado.websocket.WebSocketHandler):
	def __init__(self, request, spec_kwargs):
		tornado.websocket.WebSocketHandler.__init__(self, request, spec_kwargs)
	def open(self):
		message={};
		message["proto_type"]="chat_message"
		message["sender"]="test_chatter"
		message["chat_seq"]=1

		self.write_message(json.dumps(message))

	def on_message(self, message):
		pass

import tornado.web
from tornado.wsgi import WSGIContainer
from tornado.web import FallbackHandler, RequestHandler, Application

from wisewolf.web.main import app
from wisewolf.websocket.chatting.chat_handler import ChattingHandler

	
tr= WSGIContainer(app)

application= tornado.web.Application([(r'/ws/chat/.*', ChattingHandler),\
(r".*", FallbackHandler, dict(fallback=tr)),])

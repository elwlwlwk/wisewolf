import tornado.web
import tornado.ioloop
from tornado.wsgi import WSGIContainer
from tornado.web import FallbackHandler, RequestHandler, Application

from web.main import app
from websocket.chatting.chat_handler import ChattingHandler

	
tr= WSGIContainer(app)
application= tornado.web.Application([(r'/ws/chat/.*', ChattingHandler),\
(r".*", FallbackHandler, dict(fallback=tr)),])

if __name__== "__main__":
	application.listen(8000)
	tornado.ioloop.IOLoop.instance().start()

import tornado.web
from tornado.wsgi import WSGIContainer
from tornado.web import FallbackHandler, RequestHandler, Application

from testHandler import testHandler

application= tornado.web.Application([(r'test/ws/chat/.*', testHandler)])

import tornado.ioloop

if __name__== "__main__":
	application.listen(8888)
	tornado.ioloop.IOLoop.instance().start()

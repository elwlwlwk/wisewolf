import tornado.ioloop
from wisewolf.tornado_config import application

if __name__== "__main__":
	application.listen(7999)
	tornado.ioloop.IOLoop.instance().start()

class Config(object):
	DEBUG= False
	TESTING= False

class DevelopmentConfig(Config):
	DEBUG= True
	SECRET_KEY= "DEV_KEY"

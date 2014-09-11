from pymongo import MongoClient
from wisewolf.common.MongoDao import MongoDao

client= MongoClient()
db= client.test_wisewolf
db.authenticate("test_wisewolf","test_wisewolf")

MongoDao= MongoDao(db)

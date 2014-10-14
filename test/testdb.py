from pymongo import Connection
from wisewolf.common.MongoDao import MongoDao

db= Connection(['165.194.104.192','165.194.104.192:40001','165.194.104.192:40002']).test_wisewolf
db.authenticate("test_wisewolf","test_wisewolf")

MongoDao= MongoDao(db)

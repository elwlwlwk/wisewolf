from pymongo import MongoClient
from wisewolf.config import MONGO_AUTHENTICATE

Mongo_Wisewolf= MongoClient().wisewolf
Mongo_Wisewolf.authenticate(MONGO_AUTHENTICATE["id"],MONGO_AUTHENTICATE["passwd"])


from pymongo import MongoClient
from wisewolf.config import MONGO_AUTHENTICATE, PSQL_AUTHENTICATE, REDIS_INDEX
from redis import Redis

import psycopg2

redis_RoomSession= Redis(db= REDIS_INDEX['chatting_rooms'])
redis_UserSession= Redis(db= REDIS_INDEX['user_sessions'])

Mongo_Wisewolf= MongoClient().wisewolf
Mongo_Wisewolf.authenticate(MONGO_AUTHENTICATE["id"],MONGO_AUTHENTICATE["passwd"])

con= psycopg2.connect(database='wisewolf', user=PSQL_AUTHENTICATE["user"], password=PSQL_AUTHENTICATE["passwd"], host='165.194.104.192')
Psql_Cursor= con.cursor()

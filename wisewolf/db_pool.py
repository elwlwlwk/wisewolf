from pymongo import MongoClient
from wisewolf.config import DB_HOST, MONGO_AUTHENTICATE, PSQL_AUTHENTICATE, REDIS_INDEX
from redis import Redis, ConnectionPool

import psycopg2

#redis_RoomSession= Redis(db= REDIS_INDEX['chatting_rooms'])
#redis_UserSession= Redis(db= REDIS_INDEX['user_sessions'])

redis_UserSession= Redis(connection_pool= ConnectionPool(host=DB_HOST, db=REDIS_INDEX['chatting_rooms']))
redis_RoomSession= Redis(connection_pool= ConnectionPool(host=DB_HOST, db=REDIS_INDEX['user_sessions']))

Mongo_Wisewolf= MongoClient(host=DB_HOST).wisewolf
Mongo_Wisewolf.authenticate(MONGO_AUTHENTICATE["id"],MONGO_AUTHENTICATE["passwd"])

con= psycopg2.connect(database='wisewolf', user=PSQL_AUTHENTICATE["user"], password=PSQL_AUTHENTICATE["passwd"], host=DB_HOST)
Psql_Cursor= con.cursor()

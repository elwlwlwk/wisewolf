from pymongo import Connection
from wisewolf.config import DB_HOST, MONGO_AUTHENTICATE, PSQL_AUTHENTICATE, REDIS_INDEX
from redis import Redis, ConnectionPool

import psycopg2

#redis_RoomSession= Redis(db= REDIS_INDEX['chatting_rooms'])
#redis_UserSession= Redis(db= REDIS_INDEX['user_sessions'])

redis_UserSession= Redis(connection_pool= ConnectionPool(host=DB_HOST, db=REDIS_INDEX['user_sessions']))
redis_RoomSession= Redis(connection_pool= ConnectionPool(host=DB_HOST, db=REDIS_INDEX['chatting_rooms']))

Mongo_Wisewolf= Connection(['165.194.104.192','165.194.104.192:40001','165.194.104.192:40002']).wisewolf
Mongo_Wisewolf.authenticate(MONGO_AUTHENTICATE["id"],MONGO_AUTHENTICATE["passwd"])

con= psycopg2.connect(database='wisewolf', user=PSQL_AUTHENTICATE["user"], password=PSQL_AUTHENTICATE["passwd"], host=DB_HOST)
Psql_Cursor= con.cursor()

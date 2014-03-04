from flask import Flask
from redis import Redis
from wisewolf.config import REDIS_INDEX

app= Flask(__name__)

redis_UserSession= Redis(db=REDIS_INDEX['user_sessions'])

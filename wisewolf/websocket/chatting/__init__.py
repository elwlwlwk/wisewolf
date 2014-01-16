from redis import Redis
from wisewolf.config import REDIS_INDEX

redis_RoomSession= Redis(db= REDIS_INDEX['chatting_rooms'])

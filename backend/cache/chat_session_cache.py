import os
import dotenv
import pickle
import redis

from cache.redis import RedisConnConfig
from chat_handler import ChatHandler

dotenv.load_dotenv()


class ChatSessionCache:
    CHAT_SESSION_KEY_FORMAT = "chat-session:{session_id}"

    def __init__(self):
        redis_conn_config = RedisConnConfig(
            host=os.getenv("REDIS_HOST"),
            port=os.getenv("REDIS_PORT"),
        )
        self.redis_client = redis.StrictRedis(
            host=redis_conn_config.host,
            port=redis_conn_config.port,
            db=redis_conn_config.db,
            decode_responses=redis_conn_config.decode_responses,
        )

    def cache(self, session_id: str, instance: ChatHandler, ttl=3600):
        serialized_instance = pickle.dumps(instance)
        self.redis_client.setex(self.CHAT_SESSION_KEY_FORMAT.format(session_id=session_id), ttl, serialized_instance)

    def get(self, session_id: str):
        serialized_instance = self.redis_client.get(self.CHAT_SESSION_KEY_FORMAT.format(session_id=session_id))
        if serialized_instance:
            return pickle.loads(serialized_instance)
        return None

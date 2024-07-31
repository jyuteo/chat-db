from dataclasses import dataclass


@dataclass
class RedisConnConfig:
    host: str
    port: int = 6379
    db: int = 0
    decode_responses: bool = True

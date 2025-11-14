import redis
from redis.connection import  Connection
from src.configs.config import settings
redis_client = redis.Redis()

connection_class = Connection
redis_client.connection_pool = redis.ConnectionPool(
    **{
        "host": settings.redis_host,
        "port": settings.redis_port,
        "username": settings.redis_username,
        "password": settings.redis_password,
        "db": settings.redis_db,
        "encoding": "utf-8",
        "encoding_errors": "strict",
        "decode_responses": True,
    },
    connection_class=connection_class,
    max_connections=10
)

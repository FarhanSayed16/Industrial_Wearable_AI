"""
Industrial Wearable AI — Redis Client
Async Redis connection for JWT blacklisting and caching.
"""
import os
import redis.asyncio as redis
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Global async redis connection pool
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

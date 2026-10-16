import redis
from app.core.config import settings
import json
from typing import Optional, Any


class RedisClient:
    """Redis client wrapper for common operations."""

    def __init__(self):
        self.redis_client = None

    def connect(self):
        """Initialize Redis connection."""
        try:
            # Try to connect using REDIS_URL first
            if settings.REDIS_URL:
                self.redis_client = redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True
                )
            else:
                # Fall back to individual settings
                if settings.REDIS_PASSWORD:
                    self.redis_client = redis.Redis(
                        host=settings.REDIS_HOST,
                        port=settings.REDIS_PORT,
                        db=settings.REDIS_DB,
                        password=settings.REDIS_PASSWORD,
                        decode_responses=True,
                        socket_connect_timeout=5,
                        socket_timeout=5
                    )
                else:
                    self.redis_client = redis.Redis(
                        host=settings.REDIS_HOST,
                        port=settings.REDIS_PORT,
                        db=settings.REDIS_DB,
                        decode_responses=True,
                        socket_connect_timeout=5,
                        socket_timeout=5
                    )
            
            # Test connection
            self.redis_client.ping()
            print(f"Redis connected successfully to {settings.REDIS_HOST}:{settings.REDIS_PORT}")
        except Exception as e:
            print(f"Redis connection failed: {e}")
            self.redis_client = None

    def get_client(self):
        """Get or create Redis client."""
        if self.redis_client is None:
            self.connect()
        return self.redis_client

    def ping(self) -> bool:
        """Check if Redis is connected."""
        try:
            client = self.get_client()
            if client is None:
                return False
            return client.ping()
        except Exception as e:
            print(f"Redis ping error: {e}")
            return False

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a key-value pair in Redis."""
        try:
            client = self.get_client()
            if client is None:
                return False
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            if ttl:
                return client.setex(key, ttl, value)
            return client.set(key, value)
        except Exception as e:
            print(f"Redis set error: {e}")
            return False

    def get(self, key: str) -> Optional[Any]:
        """Get a value from Redis."""
        try:
            client = self.get_client()
            if client is None:
                return None
            value = client.get(key)
            if value is None:
                return None
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        except Exception as e:
            print(f"Redis get error: {e}")
            return None

    def delete(self, key: str) -> bool:
        """Delete a key from Redis."""
        try:
            client = self.get_client()
            if client is None:
                return False
            return client.delete(key) > 0
        except Exception as e:
            print(f"Redis delete error: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if a key exists in Redis."""
        try:
            client = self.get_client()
            if client is None:
                return False
            return client.exists(key) > 0
        except Exception as e:
            print(f"Redis exists error: {e}")
            return False

    def expire(self, key: str, ttl: int) -> bool:
        """Set expiration time for a key."""
        try:
            client = self.get_client()
            if client is None:
                return False
            return client.expire(key, ttl)
        except Exception as e:
            print(f"Redis expire error: {e}")
            return False

    def ttl(self, key: str) -> int:
        """Get remaining time to live for a key."""
        try:
            client = self.get_client()
            if client is None:
                return -1
            return client.ttl(key)
        except Exception as e:
            print(f"Redis ttl error: {e}")
            return -1

    def flushdb(self) -> bool:
        """Clear all keys in the current database."""
        try:
            client = self.get_client()
            if client is None:
                return False
            return client.flushdb()
        except Exception as e:
            print(f"Redis flushdb error: {e}")
            return False

    def close(self):
        """Close Redis connection."""
        if self.redis_client:
            self.redis_client.close()


# Global Redis client instance
redis_client = RedisClient()

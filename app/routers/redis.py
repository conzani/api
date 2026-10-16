from fastapi import APIRouter, Depends, HTTPException, Query
from app.core.redis import redis_client

router = APIRouter(prefix="/redis", tags=["Redis"])


@router.get("/health")
def redis_health():
    """Check Redis connection status."""
    try:
        is_connected = redis_client.ping()
        return {
            "status": "connected" if is_connected else "disconnected",
            "host": redis_client.get_client().connection_pool.connection_kwargs.get('host', 'unknown'),
            "port": redis_client.get_client().connection_pool.connection_kwargs.get('port', 'unknown'),
            "db": redis_client.get_client().connection_pool.connection_kwargs.get('db', 'unknown')
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Redis connection failed: {str(e)}")


@router.post("/set")
def set_redis_key(key: str = Query(...), value: str = Query(...), ttl: int = Query(None)):
    """Set a key in Redis."""
    success = redis_client.set(key, value, ttl)
    return {"success": success, "key": key, "ttl": ttl}


@router.get("/get/{key}")
def get_redis_key(key: str):
    """Get a value from Redis."""
    value = redis_client.get(key)
    return {"key": key, "value": value, "exists": value is not None}


@router.delete("/delete/{key}")
def delete_redis_key(key: str):
    """Delete a key from Redis."""
    success = redis_client.delete(key)
    return {"success": success, "key": key}


@router.post("/flush")
def flush_redis():
    """Clear all keys in the current Redis database."""
    success = redis_client.flushdb()
    return {"success": success, "message": "Database flushed"}

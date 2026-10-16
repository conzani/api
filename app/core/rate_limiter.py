from fastapi import Request, HTTPException, status
from app.core.redis import redis_client
from typing import Optional
import functools
from functools import wraps


class RateLimiter:
    """Rate limiter using Redis."""

    @staticmethod
    def is_rate_limited(
        identifier: str,
        limit: int,
        window: int = 60
    ) -> tuple[bool, int]:
        """
        Check if the identifier has exceeded the rate limit.
        
        Args:
            identifier: Unique identifier (user_id, IP, etc.)
            limit: Maximum number of requests allowed
            window: Time window in seconds (default 60)
        
        Returns:
            (is_limited, remaining_requests)
        """
        key = f"ratelimit:{identifier}"
        
        # Get current count
        current = redis_client.get(key)
        
        if current is None:
            # First request in window
            redis_client.set(key, 1, ttl=window)
            return False, limit - 1
        
        current_count = int(current)
        
        if current_count >= limit:
            return True, 0
        
        # Increment count
        redis_client.set(key, current_count + 1, ttl=window)
        return False, limit - current_count - 1

    @staticmethod
    def get_remaining(identifier: str, limit: int) -> int:
        """Get remaining requests for an identifier."""
        key = f"ratelimit:{identifier}"
        current = redis_client.get(key)
        if current is None:
            return limit
        return max(0, limit - int(current))


def rate_limit(limit: int = 100, window: int = 60):
    """
    Rate limiting decorator for FastAPI endpoints.
    
    Args:
        limit: Maximum number of requests allowed
        window: Time window in seconds (default 60)
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Try to get request from kwargs (FastAPI dependency injection)
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if request is None:
                # If we can't find the request, just proceed
                return func(*args, **kwargs)
            
            # Use IP as identifier (you could also use user_id if authenticated)
            identifier = request.client.host if request.client else "unknown"
            
            # Check rate limit
            is_limited, remaining = RateLimiter.is_rate_limited(identifier, limit, window)
            
            if is_limited:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Try again in {window} seconds."
                )
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


# FastAPI dependency for rate limiting
def check_rate_limit(request: Request, limit: int = 100, window: int = 60):
    """
    FastAPI dependency for rate limiting.
    
    Usage:
        @router.get("/endpoint", dependencies=[Depends(check_rate_limit(limit=10, window=60))])
    """
    identifier = request.client.host if request.client else "unknown"
    is_limited, remaining = RateLimiter.is_rate_limited(identifier, limit, window)
    
    if is_limited:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Try again in {window} seconds."
        )
    
    return {"remaining": remaining}


# User-specific rate limiting
def check_user_rate_limit(user_id: int, limit: int = 1000, window: int = 3600):
    """
    Rate limit by user ID (for authenticated endpoints).
    
    Usage:
        @router.get("/endpoint", dependencies=[Depends(check_user_rate_limit)])
    """
    identifier = f"user:{user_id}"
    is_limited, remaining = RateLimiter.is_rate_limited(identifier, limit, window)
    
    if is_limited:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"User rate limit exceeded. Try again in {window} seconds."
        )
    
    return {"remaining": remaining}

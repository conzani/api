from app.core.redis import redis_client
from app.core.config import settings
from typing import Optional


class TokenBlacklist:
    """JWT token blacklist using Redis."""

    @staticmethod
    def revoke_token(token: str, ttl: int = None) -> bool:
        """
        Add a token to the blacklist.
        
        Args:
            token: JWT token to blacklist
            ttl: Time to live in seconds (default to access token expiry)
        """
        key = f"blacklist:{token}"
        if ttl is None:
            ttl = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        return redis_client.set(key, "revoked", ttl=ttl)

    @staticmethod
    def is_token_blacklisted(token: str) -> bool:
        """Check if a token is blacklisted."""
        key = f"blacklist:{token}"
        return redis_client.exists(key)

    @staticmethod
    def revoke_all_user_tokens(user_id: int, ttl: int = None) -> bool:
        """
        Revoke all tokens for a user.
        
        This stores a flag that indicates all tokens for this user should be invalidated.
        """
        key = f"user_blacklist:{user_id}"
        if ttl is None:
            ttl = settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400
        return redis_client.set(key, "all", ttl=ttl)

    @staticmethod
    def is_user_token_blacklisted(user_id: int) -> bool:
        """Check if all tokens for a user are blacklisted."""
        key = f"user_blacklist:{user_id}"
        return redis_client.exists(key)

    @staticmethod
    def revoke_refresh_token_hash(hash: str, ttl: int = None) -> bool:
        """
        Revoke a specific refresh token by its hash.
        """
        key = f"refresh_blacklist:{hash}"
        if ttl is None:
            ttl = settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400
        return redis_client.set(key, "revoked", ttl=ttl)

    @staticmethod
    def is_refresh_token_blacklisted(hash: str) -> bool:
        """Check if a refresh token hash is blacklisted."""
        key = f"refresh_blacklist:{hash}"
        return redis_client.exists(key)


token_blacklist = TokenBlacklist()

from app.core.redis import redis_client
from app.core.config import settings
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
import json


class SessionManager:
    """Session manager using Redis for storage."""

    @staticmethod
    def create_session(
        user_id: int,
        refresh_token_hash: str,
        device: str,
        ip_address: str,
        expires_in_days: int = None
    ) -> str:
        """Create a new session and return session ID."""
        session_id = f"session:{user_id}"
        
        session_data = {
            "user_id": user_id,
            "refresh_token_hash": refresh_token_hash,
            "device": device,
            "ip_address": ip_address,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        
        # Calculate expiration (default to refresh token expiry)
        ttl = (expires_in_days or settings.REFRESH_TOKEN_EXPIRE_DAYS) * 86400  # Convert days to seconds
        
        redis_client.set(session_id, session_data, ttl=ttl)
        
        return session_id

    @staticmethod
    def get_session(session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data by session ID."""
        return redis_client.get(session_id)

    @staticmethod
    def get_session_by_user_id(user_id: int) -> Optional[Dict[str, Any]]:
        """Get session data by user ID (assumes single active session)."""
        pattern = f"session:{user_id}:*"
        # For simplicity, we'll use a single session key per user
        key = f"session:{user_id}"
        return redis_client.get(key)

    @staticmethod
    def update_session(
        user_id: int,
        refresh_token_hash: str,
        expires_in_days: int = None
    ) -> bool:
        """Update session with new refresh token hash."""
        key = f"session:{user_id}"
        session_data = redis_client.get(key)
        
        if not session_data:
            return False
        
        # Update the refresh token hash
        session_data["refresh_token_hash"] = refresh_token_hash
        
        # Calculate expiration
        ttl = (expires_in_days or settings.REFRESH_TOKEN_EXPIRE_DAYS) * 86400
        
        return redis_client.set(key, session_data, ttl=ttl)

    @staticmethod
    def get_user_sessions(user_id: int) -> list:
        """Get all sessions for a user."""
        pattern = f"user_sessions:{user_id}:*"
        # Note: This would require Redis SCAN or keys command, simplified for now
        # For production, you'd want to use a Redis Set for user session IDs
        return []

    @staticmethod
    def revoke_session(session_id: str) -> bool:
        """Revoke/delete a session."""
        return redis_client.delete(session_id)

    @staticmethod
    def revoke_all_user_sessions(user_id: int) -> int:
        """Revoke all sessions for a user."""
        key = f"session:{user_id}"
        return redis_client.delete(key)

    @staticmethod
    def is_session_valid(session_id: str) -> bool:
        """Check if a session is still valid."""
        return redis_client.exists(session_id)


session_manager = SessionManager()

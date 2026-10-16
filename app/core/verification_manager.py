from app.core.redis import redis_client
from app.core.config import settings
from app.core.security import hash_verification_code, verify_verification_code
from typing import Optional


class VerificationCodeManager:
    """Verification code manager using Redis with auto-expiration."""

    @staticmethod
    def store_code(
        email: str,
        code: str,
        purpose: str = "email",
        ttl: int = None
    ) -> bool:
        """
        Store a verification code in Redis with auto-expiration.
        
        Args:
            email: User's email
            code: The verification code
            purpose: Purpose of the code (email, password_reset, etc.)
            ttl: Time to live in seconds (default from settings)
        """
        if ttl is None:
            ttl = settings.VERIFICATION_CODE_EXPIRE_MINUTES * 60
        
        # Hash the code before storing
        hashed_code = hash_verification_code(code)
        key = f"verification:{purpose}:{email}"
        return redis_client.set(key, hashed_code, ttl)

    @staticmethod
    def get_code(email: str, purpose: str = "email") -> Optional[int]:
        """Get a verification code from Redis (returns hash)."""
        key = f"verification:{purpose}:{email}"
        return redis_client.get(key)

    @staticmethod
    def verify_code(email: str, code: str, purpose: str = "email") -> bool:
        """
        Verify a verification code.
        
        Returns True if code matches, False otherwise.
        """
        stored_hash = VerificationCodeManager.get_code(email, purpose)
        if stored_hash is None:
            return False
        
        # Verify the code against the stored hash
        return verify_verification_code(code, stored_hash)

    @staticmethod
    def delete_code(email: str, purpose: str = "email") -> bool:
        """Delete a verification code (after successful verification)."""
        key = f"verification:{purpose}:{email}"
        return redis_client.delete(key)

    @staticmethod
    def exists(email: str, purpose: str = "email") -> bool:
        """Check if a verification code exists for this email."""
        key = f"verification:{purpose}:{email}"
        return redis_client.exists(key)


verification_code_manager = VerificationCodeManager()

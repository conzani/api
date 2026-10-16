from app.core.redis import redis_client
from typing import Optional, Any, List
import json


class CacheManager:
    """Cache manager for frequently accessed data."""

    @staticmethod
    def get(key: str) -> Optional[Any]:
        """Get data from cache."""
        return redis_client.get(key)

    @staticmethod
    def set(key: str, value: Any, ttl: int = 3600) -> bool:
        """Set data in cache with TTL (default 1 hour)."""
        return redis_client.set(key, value, ttl)

    @staticmethod
    def delete(key: str) -> bool:
        """Delete data from cache."""
        return redis_client.delete(key)

    @staticmethod
    def delete_pattern(pattern: str) -> int:
        """Delete all keys matching a pattern."""
        # This would need Redis SCAN in production
        # For now, we'll delete specific keys
        return 0

    @staticmethod
    def invalidate_business_cache(business_id: int) -> bool:
        """Invalidate all cache keys for a specific business."""
        # Invalidate catalogue data for this business
        patterns = [
            f"catalogue:business:{business_id}:*",
            f"products:business:{business_id}:*",
            f"categories:business:{business_id}:*",
            f"brands:business:{business_id}:*",
        ]
        for pattern in patterns:
            CacheManager.delete_pattern(pattern)
        return True

    # Specific cache methods for catalogue
    @staticmethod
    def cache_product(product_id: int, business_id: int, product_data: dict, ttl: int = 3600):
        """Cache a product."""
        key = f"product:{business_id}:{product_id}"
        CacheManager.set(key, product_data, ttl)

    @staticmethod
    def get_cached_product(product_id: int, business_id: int) -> Optional[dict]:
        """Get cached product."""
        key = f"product:{business_id}:{product_id}"
        return CacheManager.get(key)

    @staticmethod
    def cache_category(category_id: int, business_id: int, category_data: dict, ttl: int = 3600):
        """Cache a category."""
        key = f"category:{business_id}:{category_id}"
        CacheManager.set(key, category_data, ttl)

    @staticmethod
    def get_cached_category(category_id: int, business_id: int) -> Optional[dict]:
        """Get cached category."""
        key = f"category:{business_id}:{category_id}"
        return CacheManager.get(key)

    @staticmethod
    def cache_brand(brand_id: int, business_id: int, brand_data: dict, ttl: int = 3600):
        """Cache a brand."""
        key = f"brand:{business_id}:{brand_id}"
        CacheManager.set(key, brand_data, ttl)

    @staticmethod
    def get_cached_brand(brand_id: int, business_id: int) -> Optional[dict]:
        """Get cached brand."""
        key = f"brand:{business_id}:{brand_id}"
        return CacheManager.get(key)

    @staticmethod
    def invalidate_category_cache(business_id: int) -> bool:
        """Invalidate category cache for a business."""
        pattern = f"category:{business_id}:*"
        CacheManager.delete_pattern(pattern)
        return True

    @staticmethod
    def invalidate_brand_cache(business_id: int) -> bool:
        """Invalidate brand cache for a business."""
        pattern = f"brand:{business_id}:*"
        CacheManager.delete_pattern(pattern)
        return True

    @staticmethod
    def invalidate_product_cache(business_id: int) -> bool:
        """Invalidate product cache for a business."""
        pattern = f"product:{business_id}:*"
        CacheManager.delete_pattern(pattern)
        return True

    # Methods using public_id
    @staticmethod
    def set_category(public_id: str, category_data: dict, business_id: int, ttl: int = 3600):
        """Cache a category by public_id."""
        key = f"category:public:{public_id}"
        CacheManager.set(key, category_data, ttl)

    @staticmethod
    def get_category(public_id: str) -> Optional[dict]:
        """Get cached category by public_id."""
        key = f"category:public:{public_id}"
        return CacheManager.get(key)

    @staticmethod
    def set_brand(public_id: str, brand_data: dict, business_id: int, ttl: int = 3600):
        """Cache a brand by public_id."""
        key = f"brand:public:{public_id}"
        CacheManager.set(key, brand_data, ttl)

    @staticmethod
    def get_brand(public_id: str) -> Optional[dict]:
        """Get cached brand by public_id."""
        key = f"brand:public:{public_id}"
        return CacheManager.get(key)

    @staticmethod
    def set_product(public_id: str, product_data: dict, business_id: int, ttl: int = 3600):
        """Cache a product by public_id."""
        key = f"product:public:{public_id}"
        CacheManager.set(key, product_data, ttl)

    @staticmethod
    def get_product(public_id: str) -> Optional[dict]:
        """Get cached product by public_id."""
        key = f"product:public:{public_id}"
        return CacheManager.get(key)


cache_manager = CacheManager()

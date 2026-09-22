"""Redis Cache Configuration for EVO-LOG SaaS"""
import redis
import json
from typing import Optional, Any
from functools import wraps
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REDIS_TTL = int(os.getenv("REDIS_TTL", "300"))  # 5 minutes default

redis_client = redis.from_url(REDIS_URL, decode_responses=True)

def cache_key(tenant_id: int, resource: str, identifier: str = "") -> str:
    """Generate a standardized cache key with tenant isolation."""
    return f"evo:tenant:{tenant_id}:{resource}:{identifier}"

def get_from_cache(key: str) -> Optional[Any]:
    """Retrieve and deserialize from Redis cache."""
    try:
        data = redis_client.get(key)
        if data:
            return json.loads(data)
    except Exception:
        pass
    return None

def set_to_cache(key: str, value: Any, ttl: int = REDIS_TTL) -> bool:
    """Serialize and store in Redis cache."""
    try:
        redis_client.setex(key, ttl, json.dumps(value))
        return True
    except Exception:
        return False

def invalidate_cache_pattern(pattern: str) -> int:
    """Invalidate all keys matching a pattern."""
    try:
        keys = redis_client.keys(pattern)
        if keys:
            return redis_client.delete(*keys)
    except Exception:
        pass
    return 0

def cached(ttl: int = REDIS_TTL):
    """Decorator for caching function results with tenant isolation."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract tenant_id from context if available
            tenant_id = kwargs.get('tenant_id') or (args[0].tenant_id if args and hasattr(args[0], 'tenant_id') else 'global')
            resource = func.__name__
            identifier = kwargs.get('identifier', '')
            
            key = cache_key(tenant_id, resource, identifier)
            cached = get_from_cache(key)
            if cached is not None:
                return cached
            
            result = func(*args, **kwargs)
            set_to_cache(key, result, ttl)
            return result
        return wrapper
    return decorator

"""
Idempotency middleware to prevent duplicate operations
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import redis
import json
import hashlib
from app.core.config import settings


class IdempotencyMiddleware(BaseHTTPMiddleware):
    """Middleware to handle idempotent requests"""
    
    def __init__(self, app, redis_url: str):
        super().__init__(app)
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
    
    async def dispatch(self, request: Request, call_next):
        # Only apply to POST, PUT, PATCH requests
        if request.method not in ["POST", "PUT", "PATCH"]:
            return await call_next(request)
        
        # Get idempotency key from header
        idempotency_key = request.headers.get("X-Idempotency-Key")
        if not idempotency_key:
            return await call_next(request)
        
        # Create cache key
        cache_key = f"idempotency:{idempotency_key}:{request.url.path}"
        
        # Check if request already processed
        try:
            cached_response = self.redis_client.get(cache_key)
            if cached_response:
                cached_data = json.loads(cached_response)
                from starlette.responses import JSONResponse
                return JSONResponse(
                    status_code=cached_data["status_code"],
                    content=cached_data.get("body", ""),
                    headers=cached_data.get("headers", {})
                )
        except Exception:
            pass  # If Redis is unavailable, continue processing
        
        # Process request
        response = await call_next(request)
        
        # Cache response for 1 hour
        if response.status_code < 400:
            try:
                response_data = {
                    "status_code": response.status_code,
                    "body": "",
                    "headers": dict(response.headers)
                }
                self.redis_client.setex(cache_key, 3600, json.dumps(response_data))
            except Exception:
                pass  # If Redis is unavailable, skip caching
        
        return response
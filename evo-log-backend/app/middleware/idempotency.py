"""
Idempotency middleware to prevent duplicate operations
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
import redis
import json
import hashlib
import base64
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


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
        
        if len(idempotency_key) > 200:
            return JSONResponse({"detail": "X-Idempotency-Key is too long"}, status_code=400)

        body = await request.body()
        async def receive_body():
            return {"type": "http.request", "body": body, "more_body": False}
        request._receive = receive_body
        fingerprint = hashlib.sha256(
            request.method.encode() + b"\0" + request.url.path.encode() + b"\0" + body
        ).hexdigest()
        auth = request.headers.get("Authorization", "")
        subject = hashlib.sha256(auth.encode()).hexdigest()[:16] if auth else "anonymous"
        cache_key = f"idempotency:v2:{subject}:{idempotency_key}"
        lock_key = f"{cache_key}:lock"

        try:
            cached_response = self.redis_client.get(cache_key)
            if cached_response:
                cached_data = json.loads(cached_response)
                if cached_data["fingerprint"] != fingerprint:
                    return JSONResponse(
                        {"detail": "Idempotency key was reused with a different request"},
                        status_code=409,
                    )
                return Response(
                    content=base64.b64decode(cached_data["body"]),
                    status_code=cached_data["status_code"],
                    headers=cached_data.get("headers", {}),
                    media_type=cached_data.get("media_type"),
                )
            if not self.redis_client.set(lock_key, "1", nx=True, ex=120):
                return JSONResponse(
                    {"detail": "An identical request is already being processed"},
                    status_code=409,
                )
        except redis.RedisError:
            return JSONResponse(
                {"detail": "Idempotency storage is unavailable"},
                status_code=503,
            )

        try:
            response = await call_next(request)
            response_body = b"".join([chunk async for chunk in response.body_iterator])
            if response.status_code < 400:
                response_data = {
                    "fingerprint": fingerprint,
                    "status_code": response.status_code,
                    "body": base64.b64encode(response_body).decode("ascii"),
                    "headers": {
                        key: value for key, value in response.headers.items()
                        if key.lower() not in {"content-length", "transfer-encoding"}
                    },
                    "media_type": response.media_type,
                }
                self.redis_client.setex(cache_key, 3600, json.dumps(response_data))
            return Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )
        finally:
            try:
                self.redis_client.delete(lock_key)
            except redis.RedisError:
                logger.warning("Failed to release idempotency lock", exc_info=True)
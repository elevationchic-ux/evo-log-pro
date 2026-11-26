from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from typing import Optional

class IdempotencyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, redis_url: Optional[str] = None):
        super().__init__(app)
        self.redis_url = redis_url

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        return response

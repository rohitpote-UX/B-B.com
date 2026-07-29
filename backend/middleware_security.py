"""
Brand Battle - Security & Rate Limiting Middlewares
Enforces security headers and Redis sliding-window rate limiting.
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
from config import settings
from redis_client import redis_client, is_redis_healthy


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Enforces standard security headers on all HTTP responses."""

    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        if settings.ENV == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            
        return response


class RedisRateLimiterMiddleware(BaseHTTPMiddleware):
    """Redis-backed sliding window rate limiter per client IP."""

    async def dispatch(self, request: Request, call_next):
        # Exclude documentation and health check paths from rate limiting
        if request.url.path in ["/health", "/", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)

        if is_redis_healthy():
            client_ip = request.client.host if request.client else "unknown"
            current_minute = int(time.time() // 60)
            key = f"rate_limit:{client_ip}:{current_minute}"

            try:
                pipe = redis_client.pipeline()
                pipe.incr(key)
                pipe.expire(key, 60)
                request_count, _ = pipe.execute()

                if request_count > settings.RATE_LIMIT_PER_MINUTE:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Rate limit exceeded. Please slow down your requests."
                    )
            except HTTPException:
                raise
            except Exception as e:
                # Log redis rate limiting error and proceed
                print(f"⚠️ Rate limiting error: {e}")

        return await call_next(request)

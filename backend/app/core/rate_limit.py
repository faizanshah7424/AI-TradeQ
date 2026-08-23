import time
from collections import defaultdict
from threading import Lock
from typing import Optional
from fastapi import Request, HTTPException, status
from app.core.config import settings

class InMemoryRateLimiter:
    """
    Thread-safe in-memory sliding window rate limiter.
    Provides immediate local rate limiting protection with seamless Redis upgradability.
    """
    def __init__(self):
        self._requests = defaultdict(list)
        self._lock = Lock()

    def is_rate_limited(self, key: str, max_requests: int, window_seconds: int = 60) -> bool:
        now = time.time()
        with self._lock:
            timestamps = self._requests[key]
            # Prune timestamps outside window
            cutoff = now - window_seconds
            self._requests[key] = [t for t in timestamps if t > cutoff]
            
            if len(self._requests[key]) >= max_requests:
                return True
            
            self._requests[key].append(now)
            return False

    def reset(self, key: Optional[str] = None):
        with self._lock:
            if key:
                self._requests.pop(key, None)
            else:
                self._requests.clear()

limiter = InMemoryRateLimiter()

def get_client_ip(request: Request) -> str:
    """Extract client IP address handling X-Forwarded-For headers securely."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "127.0.0.1"

def rate_limit_dependency(max_requests: Optional[int] = None, window_seconds: int = 60):
    """FastAPI dependency for protecting sensitive authentication endpoints."""
    def dependency(request: Request):
        limit = max_requests or settings.RATE_LIMIT_PER_MINUTE_AUTH
        client_ip = get_client_ip(request)
        endpoint = request.url.path
        key = f"{client_ip}:{endpoint}"
        
        if limiter.is_rate_limited(key, limit, window_seconds):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please slow down and try again later.",
                headers={"Retry-After": str(window_seconds)},
            )
    return dependency

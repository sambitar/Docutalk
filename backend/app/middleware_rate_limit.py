from collections import defaultdict
from time import time

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send


class SimpleRateLimitMiddleware:
    """Per-IP rate limit for mutating API routes (free-tier abuse control)."""

    def __init__(self, app: ASGIApp, limit: int = 120, window_seconds: float = 60.0):
        self.app = app
        self.limit = limit
        self.window = window_seconds
        self._hits: dict[str, list[float]] = defaultdict(list)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        method = scope.get("method", "GET")
        if method in {"POST", "PUT", "DELETE", "PATCH"}:
            client = scope.get("client")
            ip = client[0] if client else "unknown"
            now = time()
            hits = [t for t in self._hits[ip] if now - t < self.window]
            if len(hits) >= self.limit:
                response = JSONResponse(status_code=429, content={"detail": "Too many requests"})
                await response(scope, receive, send)
                return
            hits.append(now)
            self._hits[ip] = hits

        await self.app(scope, receive, send)

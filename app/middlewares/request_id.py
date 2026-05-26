"""Attach a unique request-id to every request + log timing."""

import time, uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import structlog

logger = structlog.get_logger(__name__)

class RequestIDMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        req_id = str(uuid.uuid4())
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=req_id, path=request.url.path)

        t0 = time.perf_counter()
        response = await call_next(request)
        elapsed = round((time.perf_counter() - t0) * 1000, 2)

        logger.info(
            "request",
            method=request.method,
            status=response.status_code,
            duration_ms=elapsed
        )
        response.headers["X-Request_ID"] = req_id
        return response
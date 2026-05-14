"""Request-id and access-log middleware."""
from __future__ import annotations

import time
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.utils.logging import get_logger, set_request_id

log = get_logger("app.access")


REQUEST_ID_HEADER = "X-Request-ID"


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Attach a correlation id to every request.

    Honours an inbound `X-Request-ID` header so an upstream load
    balancer or curl call can pin its own id; otherwise mints a UUID.
    The id is stamped on `request.state`, on every log record (via
    ContextVar), and on the outgoing response header.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        rid = request.headers.get(REQUEST_ID_HEADER) or str(uuid4())
        request.state.request_id = rid
        set_request_id(rid)

        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            elapsed_ms = (time.perf_counter() - start) * 1000
            log.exception(
                "%s %s · failed after %.1fms",
                request.method,
                request.url.path,
                elapsed_ms,
            )
            set_request_id(None)
            raise

        elapsed_ms = (time.perf_counter() - start) * 1000
        log.info(
            "%s %s → %s · %.1fms",
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
        )
        response.headers[REQUEST_ID_HEADER] = rid
        set_request_id(None)
        return response

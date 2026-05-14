"""Process logging configuration.

A small wrapper around the stdlib so the app and uvicorn share one
formatter and so the request-id middleware can stamp every line with a
correlation id.
"""
from __future__ import annotations

import logging
import sys
from contextvars import ContextVar
from typing import Optional

from app.config import settings


# A ContextVar lets every log call inside a single request pick up the
# correlation id without having to thread it through every function.
_request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


def set_request_id(value: Optional[str]) -> None:
    _request_id_var.set(value)


def get_request_id() -> Optional[str]:
    return _request_id_var.get()


class _RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id() or "-"
        return True


_DEFAULT_FORMAT = (
    "%(asctime)s [%(levelname)-5s] %(name)s rid=%(request_id)s %(message)s"
)


def configure_logging(level: Optional[str] = None) -> None:
    """Idempotent root logger setup.

    Honours `LOG_LEVEL` from settings; quiets uvicorn's per-request access
    log so our middleware-based access line is the canonical record.
    """
    resolved = (level or settings.log_level).upper()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(_DEFAULT_FORMAT))
    handler.addFilter(_RequestIdFilter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(resolved)

    # Keep our own loggers at the configured level…
    logging.getLogger("app").setLevel(resolved)
    # …and quiet uvicorn's own access log; we emit our own.
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)

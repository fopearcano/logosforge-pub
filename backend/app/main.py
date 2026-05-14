from __future__ import annotations

import re
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.config import settings
from app.db import init_db
from app.routers import ALL_ROUTERS
from app.utils.logging import configure_logging, get_logger
from app.utils.middleware import REQUEST_ID_HEADER, RequestIdMiddleware

log = get_logger("app.main")


def _safe_db_url(url: str) -> str:
    """Mask the password component before logging a database URL."""
    return re.sub(r"://([^:/@]+):([^@]+)@", r"://\1:***@", url)


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    log.info(
        "%s starting · env=%s · db=%s",
        settings.app_name,
        settings.environment,
        _safe_db_url(settings.database_url),
    )
    init_db()
    log.info("schema initialised")
    yield
    log.info("%s stopping", settings.app_name)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Editorial management platform for publishing houses.",
        lifespan=lifespan,
    )

    # Order matters: CORS first so preflight requests don't trip the
    # request-id log, then the request-id middleware so every entry in
    # the access log carries a correlation id.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=[REQUEST_ID_HEADER],
    )
    app.add_middleware(RequestIdMiddleware)

    for router_module in ALL_ROUTERS:
        app.include_router(router_module.router, prefix=settings.api_prefix)

    @app.exception_handler(IntegrityError)
    async def _integrity_error_handler(
        request: Request, _exc: IntegrityError
    ) -> JSONResponse:
        rid = getattr(request.state, "request_id", "-")
        log.warning("integrity error · path=%s", request.url.path)
        return JSONResponse(
            status_code=409,
            content={
                "detail": "Database constraint violation.",
                "request_id": rid,
            },
            headers={REQUEST_ID_HEADER: rid},
        )

    @app.exception_handler(Exception)
    async def _internal_error_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        # FastAPI's HTTPException is dispatched before this catch-all,
        # so anything reaching here is genuinely unexpected.
        rid = getattr(request.state, "request_id", "-")
        log.exception(
            "unhandled exception · path=%s · type=%s",
            request.url.path,
            type(exc).__name__,
        )
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error.",
                "request_id": rid,
            },
            headers={REQUEST_ID_HEADER: rid},
        )

    @app.get("/", tags=["root"], summary="Service identity")
    def root() -> dict[str, str]:
        return {
            "service": settings.app_name,
            "version": settings.app_version,
            "docs": "/docs",
        }

    return app


app = create_app()

from __future__ import annotations

from fastapi import APIRouter

from app.config import settings

router = APIRouter(prefix="/meta", tags=["meta"])


@router.get("", summary="Application metadata")
def meta() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }

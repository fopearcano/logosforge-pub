"""API routers. Each module exposes a `router` attribute mounted in main.py."""

from app.routers import health, meta

__all__ = ["health", "meta"]

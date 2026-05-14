"""API routers. Each module exposes a `router` attribute mounted in main.py."""

from app.routers import (
    auth,
    authors,
    contracts,
    editorial_notes,
    health,
    manuscripts,
    meta,
    production_items,
    reviews,
    workflow,
    workflow_events,
)

ALL_ROUTERS = (
    health,
    meta,
    auth,
    authors,
    manuscripts,
    reviews,
    workflow,
    workflow_events,
    contracts,
    production_items,
    editorial_notes,
)

__all__ = [
    "ALL_ROUTERS",
    "auth",
    "authors",
    "contracts",
    "editorial_notes",
    "health",
    "manuscripts",
    "meta",
    "production_items",
    "reviews",
    "workflow",
    "workflow_events",
]

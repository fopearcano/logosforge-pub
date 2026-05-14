"""API routers. Each module exposes a `router` attribute mounted in main.py."""

from app.routers import (
    authors,
    contracts,
    editorial_notes,
    health,
    manuscripts,
    meta,
    production_items,
    reviews,
    workflow_events,
)

ALL_ROUTERS = (
    health,
    meta,
    authors,
    manuscripts,
    reviews,
    workflow_events,
    contracts,
    production_items,
    editorial_notes,
)

__all__ = [
    "ALL_ROUTERS",
    "authors",
    "contracts",
    "editorial_notes",
    "health",
    "manuscripts",
    "meta",
    "production_items",
    "reviews",
    "workflow_events",
]

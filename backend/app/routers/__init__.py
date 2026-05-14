"""API routers. Each module exposes a `router` attribute mounted in main.py."""

from app.routers import (
    auth,
    authors,
    contracts,
    dashboard,
    editorial_notes,
    health,
    manuscripts,
    meta,
    production_items,
    production_records,
    reviews,
    search,
    workflow,
    workflow_events,
)

ALL_ROUTERS = (
    health,
    meta,
    auth,
    dashboard,
    search,
    authors,
    manuscripts,
    reviews,
    workflow,
    workflow_events,
    contracts,
    production_items,
    production_records,
    editorial_notes,
)

__all__ = [
    "ALL_ROUTERS",
    "auth",
    "authors",
    "contracts",
    "dashboard",
    "editorial_notes",
    "health",
    "manuscripts",
    "meta",
    "production_items",
    "production_records",
    "reviews",
    "search",
    "workflow",
    "workflow_events",
]

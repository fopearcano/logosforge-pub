"""API routers. Each module exposes a `router` attribute mounted in main.py."""

from types import SimpleNamespace

from app.routers import (
    ai,
    attachments,
    auth,
    authors,
    contracts,
    dashboard,
    editorial_notes,
    exports,
    health,
    knowledge,
    manuscripts,
    meta,
    production_items,
    production_records,
    reviews,
    search,
    workflow,
    workflow_events,
)

# The knowledge module exposes two routers — the main /knowledge surface
# and a manuscript-scoped one mounted under /manuscripts/{id}/entity-links.
# Both need to be included; wrap the second in a tiny namespace so the
# include loop in main.py can stay uniform.
_manuscript_links = SimpleNamespace(router=knowledge.manuscript_links_router)

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
    attachments,
    exports,
    ai,
    knowledge,
    _manuscript_links,
)

__all__ = [
    "ALL_ROUTERS",
    "ai",
    "attachments",
    "auth",
    "authors",
    "contracts",
    "dashboard",
    "editorial_notes",
    "exports",
    "health",
    "knowledge",
    "manuscripts",
    "meta",
    "production_items",
    "production_records",
    "reviews",
    "search",
    "workflow",
    "workflow_events",
]

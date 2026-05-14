"""Database seed entrypoint.

Run with::

    python -m app.seed

Seed data will be added alongside the domain models. For now this script only
ensures the schema is materialised.
"""
from __future__ import annotations

from app.db import init_db


def run() -> None:
    init_db()
    print("Schema initialised. No seed data defined yet.")


if __name__ == "__main__":
    run()

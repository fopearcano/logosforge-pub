from __future__ import annotations

from datetime import date, timedelta

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.auth.security import hash_password
from app.models import (
    Author,
    Manuscript,
    ProductionItem,
    Review,
    User,
    WorkflowEvent,
)
from app.models.enums import (
    ProductionItemStatus,
    ProductionStage,
    ReviewVerdict,
    UserRole,
    WorkflowStatus,
)


def _seed_minimal_house(session: Session) -> dict[str, object]:
    editor = User(
        email="ed@logosforge.test",
        full_name="House Editor",
        role=UserRole.EDITOR,
        hashed_password=hash_password("password"),
    )
    author = Author(full_name="Test Author", country="Test")
    session.add_all([editor, author])
    session.commit()
    session.refresh(editor)
    session.refresh(author)

    submitted = Manuscript(
        title="Pending Submission",
        author_id=author.id,
        status=WorkflowStatus.SUBMITTED,
    )
    under_review = Manuscript(
        title="In Discussion",
        author_id=author.id,
        status=WorkflowStatus.UNDER_REVIEW,
    )
    in_prepress = Manuscript(
        title="At Press",
        author_id=author.id,
        status=WorkflowStatus.PREPRESS,
    )
    in_layout = Manuscript(
        title="On the Bench",
        author_id=author.id,
        status=WorkflowStatus.LAYOUT,
    )
    published = Manuscript(
        title="Out in the World",
        author_id=author.id,
        status=WorkflowStatus.PUBLISHED,
    )
    session.add_all([submitted, under_review, in_prepress, in_layout, published])
    session.commit()
    for m in (submitted, under_review, in_prepress, in_layout, published):
        session.refresh(m)

    # A review on the under_review manuscript.
    session.add(
        Review(
            manuscript_id=under_review.id,
            reviewer_id=editor.id,
            verdict=ReviewVerdict.REVISE,
            summary="Promising. Some restructuring needed.",
            rating=4,
        )
    )

    today = date.today()
    # Production items with various due dates and states.
    session.add_all(
        [
            ProductionItem(
                manuscript_id=in_prepress.id,
                assignee_id=editor.id,
                stage=ProductionStage.PREPRESS,
                status=ProductionItemStatus.IN_PROGRESS,
                due_date=today + timedelta(days=5),
            ),
            ProductionItem(
                manuscript_id=in_layout.id,
                assignee_id=editor.id,
                stage=ProductionStage.LAYOUT,
                status=ProductionItemStatus.IN_PROGRESS,
                due_date=today - timedelta(days=2),  # overdue
            ),
            ProductionItem(
                manuscript_id=in_layout.id,
                stage=ProductionStage.COVER_DESIGN,
                status=ProductionItemStatus.DONE,
                due_date=today - timedelta(days=30),  # excluded — done
            ),
            ProductionItem(
                manuscript_id=published.id,
                stage=ProductionStage.PRINTING,
                status=ProductionItemStatus.DONE,
                due_date=today - timedelta(days=10),  # excluded — done
            ),
        ]
    )

    # Workflow events: timeline. Insert in chronological order; created_at
    # is auto-generated so order is preserved.
    session.add_all(
        [
            WorkflowEvent(
                manuscript_id=submitted.id,
                from_status=None,
                to_status=WorkflowStatus.SUBMITTED,
            ),
            WorkflowEvent(
                manuscript_id=under_review.id,
                from_status=WorkflowStatus.SUBMITTED,
                to_status=WorkflowStatus.UNDER_REVIEW,
                actor_id=editor.id,
            ),
            WorkflowEvent(
                manuscript_id=in_layout.id,
                from_status=WorkflowStatus.COVER_DESIGN,
                to_status=WorkflowStatus.LAYOUT,
                actor_id=editor.id,
                note="Re-laying after cover revisions.",
            ),
        ]
    )
    session.commit()

    return {
        "editor": editor,
        "author": author,
        "submitted": submitted,
        "under_review": under_review,
        "in_prepress": in_prepress,
        "in_layout": in_layout,
        "published": published,
    }


def test_status_counts_returns_all_statuses_even_when_empty(
    anon_client: TestClient,
) -> None:
    r = anon_client.get("/api/dashboard/status-counts")
    assert r.status_code == 200
    body = r.json()
    assert len(body) == 12
    assert {row["status"] for row in body} == {
        "submitted",
        "under_review",
        "accepted",
        "rejected",
        "development_editing",
        "copy_editing",
        "proofreading",
        "layout",
        "cover_design",
        "prepress",
        "published",
        "archived",
    }
    assert all(row["count"] == 0 for row in body)


def test_status_counts_with_data(
    anon_client: TestClient, session: Session
) -> None:
    _seed_minimal_house(session)
    body = anon_client.get("/api/dashboard/status-counts").json()
    by_status = {row["status"]: row["count"] for row in body}
    assert by_status["submitted"] == 1
    assert by_status["under_review"] == 1
    assert by_status["layout"] == 1
    assert by_status["prepress"] == 1
    assert by_status["published"] == 1
    assert by_status["archived"] == 0


def test_active_reviews_returns_under_review_manuscripts_with_latest_verdict(
    anon_client: TestClient, session: Session
) -> None:
    seeded = _seed_minimal_house(session)
    body = anon_client.get("/api/dashboard/active-reviews").json()
    assert len(body) == 1
    entry = body[0]
    assert entry["manuscript_id"] == seeded["under_review"].id
    assert entry["manuscript_title"] == "In Discussion"
    assert entry["author_name"] == "Test Author"
    assert entry["review_count"] == 1
    assert entry["latest_verdict"] == "revise"


def test_upcoming_releases_orders_by_progression(
    anon_client: TestClient, session: Session
) -> None:
    _seed_minimal_house(session)
    body = anon_client.get("/api/dashboard/upcoming-releases").json()
    statuses = [row["status"] for row in body]
    # Prepress before Layout (closer to publication first).
    assert statuses == ["prepress", "layout"]
    prepress = body[0]
    assert prepress["next_due"] is not None
    assert prepress["open_production_items"] == 1


def test_deadlines_excludes_done_and_sorts_soonest_first(
    anon_client: TestClient, session: Session
) -> None:
    _seed_minimal_house(session)
    body = anon_client.get("/api/dashboard/deadlines").json()
    assert len(body) == 2
    # Overdue layout item first (negative days_until), then prepress.
    assert body[0]["stage"] == "layout"
    assert body[0]["days_until"] < 0
    assert body[0]["assignee_name"] == "House Editor"
    assert body[1]["stage"] == "prepress"
    assert body[1]["days_until"] >= 0


def test_recent_activity_orders_newest_first_and_includes_titles(
    anon_client: TestClient, session: Session
) -> None:
    seeded = _seed_minimal_house(session)
    body = anon_client.get("/api/dashboard/recent-activity").json()
    assert len(body) == 3
    # Newest first; the layout transition was the last seeded event.
    assert body[0]["manuscript_title"] == "On the Bench"
    assert body[0]["to_status"] == "layout"
    assert body[0]["from_status"] == "cover_design"
    assert body[0]["actor_name"] == "House Editor"
    assert body[0]["note"] == "Re-laying after cover revisions."
    # Oldest event has no actor.
    last = next(b for b in body if b["manuscript_id"] == seeded["submitted"].id)
    assert last["actor_name"] is None
    assert last["from_status"] is None
    assert last["to_status"] == "submitted"


def test_dashboard_limit_query_caps_results(
    anon_client: TestClient, session: Session
) -> None:
    _seed_minimal_house(session)
    body = anon_client.get("/api/dashboard/recent-activity?limit=1").json()
    assert len(body) == 1


def test_dashboard_endpoints_are_public(anon_client: TestClient) -> None:
    # Anonymous reads work, like the other GET endpoints.
    for path in (
        "/api/dashboard/status-counts",
        "/api/dashboard/active-reviews",
        "/api/dashboard/upcoming-releases",
        "/api/dashboard/deadlines",
        "/api/dashboard/recent-activity",
    ):
        r = anon_client.get(path)
        assert r.status_code == 200, path

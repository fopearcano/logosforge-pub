from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlmodel import Session, select

from app.auth.security import hash_password
from app.models import (
    Author,
    Contract,
    ContractStatus,
    EditorialNote,
    EditorialNoteKind,
    Manuscript,
    ProductionItem,
    ProductionItemStatus,
    ProductionStage,
    Review,
    ReviewVerdict,
    User,
    UserRole,
    WorkflowEvent,
    WorkflowStatus,
)


def _seed_minimal(session: Session) -> tuple[User, Author, Manuscript]:
    editor = User(
        email="editor@logosforge.test",
        full_name="Test Editor",
        role=UserRole.EDITOR,
        hashed_password=hash_password("password"),
    )
    author = Author(full_name="Test Author", country="Nowhere")
    session.add_all([editor, author])
    session.commit()
    session.refresh(editor)
    session.refresh(author)

    manuscript = Manuscript(
        title="Untitled Folio",
        author_id=author.id,
        status=WorkflowStatus.SUBMITTED,
        word_count=10000,
    )
    session.add(manuscript)
    session.commit()
    session.refresh(manuscript)
    return editor, author, manuscript


def test_base_entity_timestamps_and_id(session: Session) -> None:
    user = User(
        email="x@y.z", full_name="X", hashed_password=hash_password("password")
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    assert isinstance(user.id, str) and len(user.id) == 36
    assert isinstance(user.created_at, datetime)
    assert isinstance(user.updated_at, datetime)


def test_manuscript_with_full_graph_roundtrip(session: Session) -> None:
    editor, author, manuscript = _seed_minimal(session)

    session.add_all(
        [
            WorkflowEvent(
                manuscript_id=manuscript.id,
                actor_id=editor.id,
                from_status=WorkflowStatus.SUBMITTED,
                to_status=WorkflowStatus.UNDER_REVIEW,
            ),
            Review(
                manuscript_id=manuscript.id,
                reviewer_id=editor.id,
                verdict=ReviewVerdict.ACCEPT,
                summary="ok",
                rating=4,
            ),
            EditorialNote(
                manuscript_id=manuscript.id,
                author_user_id=editor.id,
                kind=EditorialNoteKind.LINE,
                body="Tighten the opening.",
            ),
            ProductionItem(
                manuscript_id=manuscript.id,
                assignee_id=editor.id,
                stage=ProductionStage.LAYOUT,
                status=ProductionItemStatus.IN_PROGRESS,
            ),
            Contract(
                manuscript_id=manuscript.id,
                author_id=author.id,
                status=ContractStatus.DRAFT,
                advance_amount=Decimal("1200.00"),
                royalty_rate=0.10,
            ),
        ]
    )
    session.commit()

    fetched = session.exec(
        select(Manuscript).where(Manuscript.id == manuscript.id)
    ).one()

    assert fetched.author.full_name == "Test Author"
    assert len(fetched.workflow_events) == 1
    assert fetched.workflow_events[0].to_status == WorkflowStatus.UNDER_REVIEW
    assert len(fetched.reviews) == 1
    assert fetched.reviews[0].verdict == ReviewVerdict.ACCEPT
    assert len(fetched.editorial_notes) == 1
    assert len(fetched.production_items) == 1
    assert fetched.production_items[0].assignee.id == editor.id
    assert len(fetched.contracts) == 1
    assert fetched.contracts[0].advance_amount == Decimal("1200.00")


def test_user_reverse_relationships(session: Session) -> None:
    editor, _, manuscript = _seed_minimal(session)
    session.add(
        Review(
            manuscript_id=manuscript.id,
            reviewer_id=editor.id,
            verdict=ReviewVerdict.REVISE,
            summary="needs work",
        )
    )
    session.commit()
    session.refresh(editor)

    assert len(editor.reviews) == 1
    assert editor.reviews[0].manuscript_id == manuscript.id


def test_workflow_event_nullable_actor(session: Session) -> None:
    _, _, manuscript = _seed_minimal(session)
    event = WorkflowEvent(
        manuscript_id=manuscript.id,
        actor_id=None,
        from_status=None,
        to_status=WorkflowStatus.SUBMITTED,
    )
    session.add(event)
    session.commit()
    session.refresh(event)

    assert event.actor is None
    assert event.from_status is None
    assert event.to_status == WorkflowStatus.SUBMITTED


def test_enum_persistence_roundtrip(session: Session) -> None:
    _, _, manuscript = _seed_minimal(session)
    manuscript.status = WorkflowStatus.COVER_DESIGN
    session.add(manuscript)
    session.commit()

    session.expire_all()
    fetched = session.exec(
        select(Manuscript).where(Manuscript.id == manuscript.id)
    ).one()
    assert fetched.status == WorkflowStatus.COVER_DESIGN


def test_user_email_unique(session: Session) -> None:
    import pytest
    from sqlalchemy.exc import IntegrityError

    hp = hash_password("password")
    session.add(User(email="dup@logosforge.test", full_name="A", hashed_password=hp))
    session.commit()
    session.add(User(email="dup@logosforge.test", full_name="B", hashed_password=hp))
    with pytest.raises(IntegrityError):
        session.commit()

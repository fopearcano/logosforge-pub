"""Database seed entrypoint.

Run with::

    python -m app.seed

Idempotent: if the users table is already populated the seed is a no-op.
"""
from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from sqlmodel import Session, select

from app.auth.security import hash_password
from app.db import engine, init_db
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
from app.models.base import utcnow

# A single demo password keyed for every seeded user; documented in the README.
DEMO_PASSWORD = "logosforge"


def _user(email: str, full_name: str, role: UserRole) -> User:
    return User(
        email=email,
        full_name=full_name,
        role=role,
        hashed_password=hash_password(DEMO_PASSWORD),
    )


def _seed_users(session: Session) -> dict[str, User]:
    users = {
        # Editorial leadership and editors.
        "helena": _user("helena.pryce@logosforge.local", "Helena Pryce", UserRole.ADMIN),
        "jonas": _user("jonas.marten@logosforge.local", "Jonas Mårten", UserRole.EDITOR),
        "cecilia": _user("cecilia.dore@logosforge.local", "Cecilia Doré", UserRole.EDITOR),
        "tomas": _user("tomas.aribau@logosforge.local", "Tomás Aribau", UserRole.EDITOR),
        "ruth": _user("ruth.engstrom@logosforge.local", "Ruth Engström", UserRole.EDITOR),
        # External / structural reviewer.
        "bartholomew": _user(
            "bartholomew.krause@logosforge.local",
            "Bartholomew Krause",
            UserRole.REVIEWER,
        ),
        # Production.
        "kazu": _user(
            "kazu.fujita@logosforge.local", "Kazu Fujita", UserRole.PRODUCTION_MANAGER
        ),
        "ines": _user(
            "ines.harlan@logosforge.local", "Inés Harlan", UserRole.PRODUCTION_MANAGER
        ),
        # Marketing and archive.
        "mireille": _user(
            "mireille.vance@logosforge.local", "Mireille Vance", UserRole.MARKETING
        ),
        "olesya": _user(
            "olesya.kestral@logosforge.local", "Olesya Kestral", UserRole.ARCHIVE_READER
        ),
    }
    session.add_all(users.values())
    session.commit()
    for u in users.values():
        session.refresh(u)
    return users


def _seed_authors(session: Session) -> dict[str, Author]:
    authors = {
        "aldoria": Author(
            full_name="Iris Aldoria",
            email="iris.aldoria@example.org",
            country="Portugal",
            biography="Essayist and cartographer of inland seas; previous fellow at the Lisbon Atheneum.",
        ),
        "veldt": Author(
            full_name="Marcus Veldt",
            email="marcus.veldt@example.org",
            country="Netherlands",
            biography="Novelist of correspondences and provincial life.",
        ),
        "carrick": Author(
            full_name="Saoirse Carrick",
            email="saoirse.carrick@example.org",
            country="Ireland",
            biography="Short-form writer; debut novella under consideration.",
        ),
        "bellecour": Author(
            full_name="Diane Bellecour",
            email="d.bellecour@example.org",
            country="France",
            biography="Naturalist; lecturer at the Muséum, writing in the Buffon tradition.",
        ),
        "tanigawa": Author(
            full_name="Hideo Tanigawa",
            email="h.tanigawa@example.org",
            country="Japan",
            biography="Debut novelist; trained as a typographer in Kyoto.",
        ),
    }
    session.add_all(authors.values())
    session.commit()
    for a in authors.values():
        session.refresh(a)
    return authors


def _seed_manuscripts(
    session: Session, authors: dict[str, Author]
) -> dict[str, Manuscript]:
    manuscripts = {
        "salt_atlases": Manuscript(
            title="The Salt Atlases",
            subtitle="A cartography of inland seas",
            synopsis=(
                "Twelve essays on the inland seas of Europe and the librarians "
                "who mapped them."
            ),
            genre="Essays",
            word_count=68200,
            status=WorkflowStatus.PUBLISHED,
            author_id=authors["aldoria"].id,
        ),
        "letters_dim": Manuscript(
            title="Letters to a Dim Province",
            synopsis=(
                "An epistolary novel set in a forgotten provincial capital at "
                "the turn of a century."
            ),
            genre="Fiction",
            word_count=92400,
            status=WorkflowStatus.COPY_EDITING,
            author_id=authors["veldt"].id,
        ),
        "silent_workshop": Manuscript(
            title="The Silent Workshop",
            synopsis=(
                "A novella concerning a printer who corresponds for forty years "
                "with a binder he never meets."
            ),
            genre="Fiction",
            word_count=41800,
            status=WorkflowStatus.UNDER_REVIEW,
            author_id=authors["carrick"].id,
        ),
        "algebra_birds": Manuscript(
            title="Algebra of Birds",
            synopsis=(
                "A natural philosophy of flock formation, written in the "
                "tradition of Buffon."
            ),
            genre="Natural history",
            word_count=54100,
            status=WorkflowStatus.DEVELOPMENT_EDITING,
            author_id=authors["bellecour"].id,
        ),
        "quintus": Manuscript(
            title="Quintus, the Foundry",
            synopsis=(
                "A debut novel concerning a typefounder in late "
                "nineteenth-century Kyoto."
            ),
            genre="Fiction",
            word_count=78900,
            status=WorkflowStatus.SUBMITTED,
            author_id=authors["tanigawa"].id,
        ),
    }
    session.add_all(manuscripts.values())
    session.commit()
    for m in manuscripts.values():
        session.refresh(m)
    return manuscripts


def _event(
    manuscript: Manuscript,
    to_status: WorkflowStatus,
    *,
    from_status: WorkflowStatus | None = None,
    actor: User | None = None,
    note: str | None = None,
) -> WorkflowEvent:
    return WorkflowEvent(
        manuscript_id=manuscript.id,
        actor_id=actor.id if actor else None,
        from_status=from_status,
        to_status=to_status,
        note=note,
    )


def _seed_workflow_events(
    session: Session,
    manuscripts: dict[str, Manuscript],
    users: dict[str, User],
) -> None:
    events: list[WorkflowEvent] = []

    # The Salt Atlases — the full editorial journey through to publication.
    salt = manuscripts["salt_atlases"]
    salt_journey: list[tuple[WorkflowStatus | None, WorkflowStatus, User | None]] = [
        (None, WorkflowStatus.SUBMITTED, None),
        (WorkflowStatus.SUBMITTED, WorkflowStatus.UNDER_REVIEW, users["jonas"]),
        (WorkflowStatus.UNDER_REVIEW, WorkflowStatus.ACCEPTED, users["helena"]),
        (WorkflowStatus.ACCEPTED, WorkflowStatus.DEVELOPMENT_EDITING, users["cecilia"]),
        (WorkflowStatus.DEVELOPMENT_EDITING, WorkflowStatus.COPY_EDITING, users["tomas"]),
        (WorkflowStatus.COPY_EDITING, WorkflowStatus.PROOFREADING, users["ruth"]),
        (WorkflowStatus.PROOFREADING, WorkflowStatus.LAYOUT, users["kazu"]),
        (WorkflowStatus.LAYOUT, WorkflowStatus.COVER_DESIGN, users["kazu"]),
        (WorkflowStatus.COVER_DESIGN, WorkflowStatus.PREPRESS, users["ines"]),
        (WorkflowStatus.PREPRESS, WorkflowStatus.PUBLISHED, users["ines"]),
    ]
    for prev, nxt, actor in salt_journey:
        events.append(_event(salt, nxt, from_status=prev, actor=actor))

    # Letters to a Dim Province — through to copy editing.
    letters = manuscripts["letters_dim"]
    for prev, nxt, actor in [
        (None, WorkflowStatus.SUBMITTED, None),
        (WorkflowStatus.SUBMITTED, WorkflowStatus.UNDER_REVIEW, users["jonas"]),
        (WorkflowStatus.UNDER_REVIEW, WorkflowStatus.ACCEPTED, users["helena"]),
        (WorkflowStatus.ACCEPTED, WorkflowStatus.DEVELOPMENT_EDITING, users["cecilia"]),
        (WorkflowStatus.DEVELOPMENT_EDITING, WorkflowStatus.COPY_EDITING, users["tomas"]),
    ]:
        events.append(_event(letters, nxt, from_status=prev, actor=actor))

    # The Silent Workshop — currently under review.
    workshop = manuscripts["silent_workshop"]
    events.append(_event(workshop, WorkflowStatus.SUBMITTED))
    events.append(
        _event(
            workshop,
            WorkflowStatus.UNDER_REVIEW,
            from_status=WorkflowStatus.SUBMITTED,
            actor=users["cecilia"],
        )
    )

    # Algebra of Birds — in development editing.
    birds = manuscripts["algebra_birds"]
    for prev, nxt, actor in [
        (None, WorkflowStatus.SUBMITTED, None),
        (WorkflowStatus.SUBMITTED, WorkflowStatus.UNDER_REVIEW, users["jonas"]),
        (WorkflowStatus.UNDER_REVIEW, WorkflowStatus.ACCEPTED, users["helena"]),
        (WorkflowStatus.ACCEPTED, WorkflowStatus.DEVELOPMENT_EDITING, users["cecilia"]),
    ]:
        events.append(_event(birds, nxt, from_status=prev, actor=actor))

    # Quintus — newly arrived.
    events.append(_event(manuscripts["quintus"], WorkflowStatus.SUBMITTED))

    session.add_all(events)
    session.commit()


def _seed_reviews(
    session: Session,
    manuscripts: dict[str, Manuscript],
    users: dict[str, User],
) -> None:
    reviews = [
        Review(
            manuscript_id=manuscripts["silent_workshop"].id,
            reviewer_id=users["jonas"].id,
            verdict=ReviewVerdict.REVISE,
            summary=(
                "A spare, beautifully restrained novella. The middle third "
                "drifts; the closing letters should arrive earlier."
            ),
            rating=4,
        ),
        Review(
            manuscript_id=manuscripts["silent_workshop"].id,
            reviewer_id=users["cecilia"].id,
            verdict=ReviewVerdict.ACCEPT,
            summary="An assured debut, ready with minor structural notes.",
            rating=4,
        ),
        Review(
            manuscript_id=manuscripts["algebra_birds"].id,
            reviewer_id=users["jonas"].id,
            verdict=ReviewVerdict.ACCEPT,
            summary=(
                "Original synthesis. The Buffon framing is earned. Recommend "
                "acceptance with light development work."
            ),
            rating=5,
        ),
        Review(
            manuscript_id=manuscripts["letters_dim"].id,
            reviewer_id=users["helena"].id,
            verdict=ReviewVerdict.ACCEPT,
            summary="Marquee voice. Proceeding to acquisition.",
            rating=5,
        ),
    ]
    session.add_all(reviews)
    session.commit()


def _seed_contracts(
    session: Session,
    manuscripts: dict[str, Manuscript],
    authors: dict[str, Author],
) -> None:
    contracts = [
        Contract(
            manuscript_id=manuscripts["salt_atlases"].id,
            author_id=authors["aldoria"].id,
            status=ContractStatus.SIGNED,
            advance_amount=Decimal("4500.00"),
            royalty_rate=0.12,
            currency="EUR",
            signed_at=utcnow() - timedelta(days=300),
            terms="Standard trade contract, first edition only.",
        ),
        Contract(
            manuscript_id=manuscripts["letters_dim"].id,
            author_id=authors["veldt"].id,
            status=ContractStatus.SIGNED,
            advance_amount=Decimal("7500.00"),
            royalty_rate=0.15,
            currency="EUR",
            signed_at=utcnow() - timedelta(days=180),
        ),
        Contract(
            manuscript_id=manuscripts["algebra_birds"].id,
            author_id=authors["bellecour"].id,
            status=ContractStatus.DRAFT,
            advance_amount=Decimal("3000.00"),
            royalty_rate=0.10,
            currency="EUR",
        ),
    ]
    session.add_all(contracts)
    session.commit()


def _seed_production_items(
    session: Session,
    manuscripts: dict[str, Manuscript],
    users: dict[str, User],
) -> None:
    today = date.today()
    items = [
        ProductionItem(
            manuscript_id=manuscripts["salt_atlases"].id,
            assignee_id=users["kazu"].id,
            stage=ProductionStage.COVER_DESIGN,
            status=ProductionItemStatus.DONE,
            due_date=today - timedelta(days=80),
            notes="Linen wrap, foil debossed title; signed off.",
        ),
        ProductionItem(
            manuscript_id=manuscripts["salt_atlases"].id,
            assignee_id=users["ines"].id,
            stage=ProductionStage.PRINTING,
            status=ProductionItemStatus.DONE,
            due_date=today - timedelta(days=35),
        ),
        ProductionItem(
            manuscript_id=manuscripts["letters_dim"].id,
            assignee_id=users["kazu"].id,
            stage=ProductionStage.LAYOUT,
            status=ProductionItemStatus.IN_PROGRESS,
            due_date=today + timedelta(days=21),
            notes="Twelve-point Garamond, generous margins; first proofs next week.",
        ),
        ProductionItem(
            manuscript_id=manuscripts["letters_dim"].id,
            assignee_id=users["kazu"].id,
            stage=ProductionStage.COVER_DESIGN,
            status=ProductionItemStatus.PENDING,
            due_date=today + timedelta(days=45),
        ),
    ]
    session.add_all(items)
    session.commit()


def _seed_editorial_notes(
    session: Session,
    manuscripts: dict[str, Manuscript],
    users: dict[str, User],
) -> None:
    notes = [
        EditorialNote(
            manuscript_id=manuscripts["silent_workshop"].id,
            author_user_id=users["cecilia"].id,
            kind=EditorialNoteKind.STRUCTURAL,
            body=(
                "Consider compressing the central correspondence into a single "
                "dated sequence; the present arrangement frays the through-line."
            ),
            pinned=True,
        ),
        EditorialNote(
            manuscript_id=manuscripts["algebra_birds"].id,
            author_user_id=users["jonas"].id,
            kind=EditorialNoteKind.GENERAL,
            body=(
                "The mathematical appendices want a separate fold-out plate; "
                "coordinate with design before copy editing begins."
            ),
        ),
        EditorialNote(
            manuscript_id=manuscripts["letters_dim"].id,
            author_user_id=users["tomas"].id,
            kind=EditorialNoteKind.LINE,
            body=(
                "Pass two complete; queries deferred to author. Awaiting "
                "clarification on chapter eleven."
            ),
        ),
    ]
    session.add_all(notes)
    session.commit()


def run() -> None:
    init_db()
    with Session(engine) as session:
        if session.exec(select(User)).first() is not None:
            print("Seed skipped: database already populated.")
            return

        users = _seed_users(session)
        authors = _seed_authors(session)
        manuscripts = _seed_manuscripts(session, authors)
        _seed_workflow_events(session, manuscripts, users)
        _seed_reviews(session, manuscripts, users)
        _seed_contracts(session, manuscripts, authors)
        _seed_production_items(session, manuscripts, users)
        _seed_editorial_notes(session, manuscripts, users)

    print(
        "Seeded LOGOSFORGE: "
        f"{len(users)} users (password '{DEMO_PASSWORD}' for all), "
        f"{len(authors)} authors, {len(manuscripts)} manuscripts, "
        "with reviews, workflow events, contracts, production items and notes."
    )


if __name__ == "__main__":
    run()

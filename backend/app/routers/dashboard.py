from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.db import get_session
from app.models import Manuscript, ProductionItem, WorkflowEvent
from app.models.enums import ProductionItemStatus, WorkflowStatus
from app.schemas.dashboard import (
    ActiveReviewSummary,
    ActivityEntry,
    DeadlineEntry,
    StatusCount,
    UpcomingRelease,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


UPCOMING_STATUSES: tuple[WorkflowStatus, ...] = (
    WorkflowStatus.LAYOUT,
    WorkflowStatus.COVER_DESIGN,
    WorkflowStatus.PREPRESS,
)

# Closer-to-publication first.
_RELEASE_PROGRESSION: dict[WorkflowStatus, int] = {
    WorkflowStatus.PREPRESS: 0,
    WorkflowStatus.COVER_DESIGN: 1,
    WorkflowStatus.LAYOUT: 2,
}


@router.get(
    "/status-counts",
    response_model=list[StatusCount],
    summary="Manuscripts grouped by workflow status",
)
def status_counts(session: Session = Depends(get_session)) -> list[StatusCount]:
    rows = session.exec(
        select(Manuscript.status, func.count(Manuscript.id)).group_by(Manuscript.status)
    ).all()
    counts: dict[WorkflowStatus, int] = dict(rows)
    return [
        StatusCount(status=status, count=counts.get(status, 0))
        for status in WorkflowStatus
    ]


@router.get(
    "/active-reviews",
    response_model=list[ActiveReviewSummary],
    summary="Manuscripts currently under review, with latest review verdict",
)
def active_reviews(
    session: Session = Depends(get_session),
    limit: int = Query(20, ge=1, le=100),
) -> list[ActiveReviewSummary]:
    manuscripts = list(
        session.exec(
            select(Manuscript)
            .where(Manuscript.status == WorkflowStatus.UNDER_REVIEW)
            .options(
                selectinload(Manuscript.author),
                selectinload(Manuscript.reviews),
            )
            .order_by(Manuscript.updated_at.desc())
            .limit(limit)
        ).all()
    )

    summaries: list[ActiveReviewSummary] = []
    for m in manuscripts:
        reviews = sorted(m.reviews, key=lambda r: r.created_at, reverse=True)
        latest = reviews[0] if reviews else None
        summaries.append(
            ActiveReviewSummary(
                manuscript_id=m.id,
                manuscript_title=m.title,
                author_name=m.author.full_name,
                review_count=len(reviews),
                latest_verdict=latest.verdict if latest else None,
                latest_review_at=latest.created_at if latest else None,
            )
        )
    return summaries


@router.get(
    "/upcoming-releases",
    response_model=list[UpcomingRelease],
    summary="Manuscripts in late-production stages, soonest to print first",
)
def upcoming_releases(
    session: Session = Depends(get_session),
    limit: int = Query(20, ge=1, le=100),
) -> list[UpcomingRelease]:
    manuscripts = list(
        session.exec(
            select(Manuscript)
            .where(Manuscript.status.in_(UPCOMING_STATUSES))
            .options(
                selectinload(Manuscript.author),
                selectinload(Manuscript.production_items),
            )
            .limit(limit)
        ).all()
    )
    manuscripts.sort(key=lambda m: _RELEASE_PROGRESSION.get(m.status, 99))

    releases: list[UpcomingRelease] = []
    for m in manuscripts:
        open_items = [
            p for p in m.production_items if p.status != ProductionItemStatus.DONE
        ]
        with_due = [p.due_date for p in open_items if p.due_date is not None]
        next_due = min(with_due) if with_due else None
        releases.append(
            UpcomingRelease(
                manuscript_id=m.id,
                title=m.title,
                author_name=m.author.full_name,
                status=m.status,
                next_due=next_due,
                open_production_items=len(open_items),
            )
        )
    return releases


@router.get(
    "/deadlines",
    response_model=list[DeadlineEntry],
    summary="Open production items with due dates, soonest first",
)
def deadlines(
    session: Session = Depends(get_session),
    limit: int = Query(20, ge=1, le=100),
) -> list[DeadlineEntry]:
    items = list(
        session.exec(
            select(ProductionItem)
            .where(ProductionItem.due_date.is_not(None))
            .where(ProductionItem.status != ProductionItemStatus.DONE)
            .options(
                selectinload(ProductionItem.manuscript),
                selectinload(ProductionItem.assignee),
            )
            .order_by(ProductionItem.due_date.asc())
            .limit(limit)
        ).all()
    )
    today = date.today()
    return [
        DeadlineEntry(
            production_item_id=i.id,
            manuscript_id=i.manuscript_id,
            manuscript_title=i.manuscript.title,
            stage=i.stage,
            status=i.status,
            assignee_name=i.assignee.full_name if i.assignee else None,
            due_date=i.due_date,
            days_until=(i.due_date - today).days,
        )
        for i in items
        if i.due_date is not None
    ]


@router.get(
    "/recent-activity",
    response_model=list[ActivityEntry],
    summary="Recent workflow transitions across the house",
)
def recent_activity(
    session: Session = Depends(get_session),
    limit: int = Query(20, ge=1, le=100),
) -> list[ActivityEntry]:
    events = list(
        session.exec(
            select(WorkflowEvent)
            .options(
                selectinload(WorkflowEvent.manuscript),
                selectinload(WorkflowEvent.actor),
            )
            .order_by(WorkflowEvent.created_at.desc())
            .limit(limit)
        ).all()
    )
    return [
        ActivityEntry(
            event_id=e.id,
            manuscript_id=e.manuscript_id,
            manuscript_title=e.manuscript.title,
            actor_id=e.actor_id,
            actor_name=e.actor.full_name if e.actor is not None else None,
            from_status=e.from_status,
            to_status=e.to_status,
            note=e.note,
            occurred_at=e.created_at,
        )
        for e in events
    ]

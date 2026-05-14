from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session, select

from app.db import get_session
from app.models import Manuscript, Review, User
from app.schemas import ReviewCreate, ReviewRead, ReviewUpdate
from app.utils import (
    Page,
    PageParams,
    apply_patch,
    ensure_exists,
    get_or_404,
    page_params,
    paginate,
)

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("", response_model=Page[ReviewRead])
def list_reviews(
    session: Session = Depends(get_session),
    params: PageParams = Depends(page_params),
    manuscript_id: Optional[str] = Query(default=None),
    reviewer_id: Optional[str] = Query(default=None),
) -> Page[ReviewRead]:
    stmt = select(Review)
    if manuscript_id is not None:
        stmt = stmt.where(Review.manuscript_id == manuscript_id)
    if reviewer_id is not None:
        stmt = stmt.where(Review.reviewer_id == reviewer_id)
    stmt = stmt.order_by(Review.created_at.desc())

    items, total = paginate(session, stmt, params)
    return Page[ReviewRead](
        items=[ReviewRead.model_validate(i) for i in items],
        total=total,
        skip=params.skip,
        limit=params.limit,
    )


@router.get("/{review_id}", response_model=ReviewRead)
def get_review(review_id: str, session: Session = Depends(get_session)) -> Review:
    return get_or_404(session, Review, review_id, name="Review")


@router.post("", response_model=ReviewRead, status_code=status.HTTP_201_CREATED)
def create_review(
    payload: ReviewCreate, session: Session = Depends(get_session)
) -> Review:
    ensure_exists(session, Manuscript, payload.manuscript_id, name="Manuscript")
    ensure_exists(session, User, payload.reviewer_id, name="User")
    review = Review(**payload.model_dump())
    session.add(review)
    session.commit()
    session.refresh(review)
    return review


@router.patch("/{review_id}", response_model=ReviewRead)
def update_review(
    review_id: str,
    payload: ReviewUpdate,
    session: Session = Depends(get_session),
) -> Review:
    review = get_or_404(session, Review, review_id, name="Review")
    apply_patch(review, payload)
    session.add(review)
    session.commit()
    session.refresh(review)
    return review


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(review_id: str, session: Session = Depends(get_session)):
    review = get_or_404(session, Review, review_id, name="Review")
    session.delete(review)
    session.commit()

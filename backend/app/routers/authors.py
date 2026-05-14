from __future__ import annotations

from enum import Enum
from typing import Literal

from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session, select

from app.auth import ADMIN_ONLY, AUTHED
from app.db import get_session
from app.models import Author
from app.schemas import AuthorCreate, AuthorRead, AuthorUpdate
from app.utils import Page, PageParams, apply_patch, get_or_404, page_params, paginate

router = APIRouter(prefix="/authors", tags=["authors"])


class AuthorSortBy(str, Enum):
    FULL_NAME = "full_name"
    COUNTRY = "country"
    CREATED_AT = "created_at"


_AUTHOR_SORT_COLUMNS = {
    AuthorSortBy.FULL_NAME: Author.full_name,
    AuthorSortBy.COUNTRY: Author.country,
    AuthorSortBy.CREATED_AT: Author.created_at,
}


@router.get("", response_model=Page[AuthorRead])
def list_authors(
    session: Session = Depends(get_session),
    params: PageParams = Depends(page_params),
    sort_by: AuthorSortBy = Query(
        default=AuthorSortBy.FULL_NAME, description="Field to order results by"
    ),
    sort_dir: Literal["asc", "desc"] = Query(
        default="asc", description="Sort direction"
    ),
) -> Page[AuthorRead]:
    column = _AUTHOR_SORT_COLUMNS[sort_by]
    stmt = select(Author).order_by(
        column.desc() if sort_dir == "desc" else column.asc()
    )
    items, total = paginate(session, stmt, params)
    return Page[AuthorRead](
        items=[AuthorRead.model_validate(i) for i in items],
        total=total,
        skip=params.skip,
        limit=params.limit,
    )


@router.get("/{author_id}", response_model=AuthorRead)
def get_author(author_id: str, session: Session = Depends(get_session)) -> Author:
    return get_or_404(session, Author, author_id, name="Author")


@router.post(
    "",
    response_model=AuthorRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=AUTHED,
)
def create_author(
    payload: AuthorCreate, session: Session = Depends(get_session)
) -> Author:
    author = Author(**payload.model_dump())
    session.add(author)
    session.commit()
    session.refresh(author)
    return author


@router.patch("/{author_id}", response_model=AuthorRead, dependencies=AUTHED)
def update_author(
    author_id: str,
    payload: AuthorUpdate,
    session: Session = Depends(get_session),
) -> Author:
    author = get_or_404(session, Author, author_id, name="Author")
    apply_patch(author, payload)
    session.add(author)
    session.commit()
    session.refresh(author)
    return author


@router.delete(
    "/{author_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=ADMIN_ONLY,
)
def delete_author(author_id: str, session: Session = Depends(get_session)):
    author = get_or_404(session, Author, author_id, name="Author")
    session.delete(author)
    session.commit()

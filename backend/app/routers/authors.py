from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select

from app.db import get_session
from app.models import Author
from app.schemas import AuthorCreate, AuthorRead, AuthorUpdate
from app.utils import Page, PageParams, apply_patch, get_or_404, page_params, paginate

router = APIRouter(prefix="/authors", tags=["authors"])


@router.get("", response_model=Page[AuthorRead])
def list_authors(
    session: Session = Depends(get_session),
    params: PageParams = Depends(page_params),
) -> Page[AuthorRead]:
    stmt = select(Author).order_by(Author.full_name)
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


@router.post("", response_model=AuthorRead, status_code=status.HTTP_201_CREATED)
def create_author(
    payload: AuthorCreate, session: Session = Depends(get_session)
) -> Author:
    author = Author(**payload.model_dump())
    session.add(author)
    session.commit()
    session.refresh(author)
    return author


@router.patch("/{author_id}", response_model=AuthorRead)
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


@router.delete("/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_author(author_id: str, session: Session = Depends(get_session)):
    author = get_or_404(session, Author, author_id, name="Author")
    session.delete(author)
    session.commit()

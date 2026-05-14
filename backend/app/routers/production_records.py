from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.auth import ADMIN_ONLY, AUTHED
from app.db import get_session
from app.models import Manuscript, ProductionRecord
from app.schemas import (
    ProductionRecordCreate,
    ProductionRecordDetail,
    ProductionRecordRead,
    ProductionRecordUpdate,
)
from app.utils import (
    Page,
    PageParams,
    apply_patch,
    ensure_exists,
    get_or_404,
    page_params,
    paginate,
)

router = APIRouter(prefix="/production-records", tags=["production_records"])


def _detail(record: ProductionRecord) -> ProductionRecordDetail:
    manuscript = record.manuscript
    return ProductionRecordDetail(
        id=record.id,
        created_at=record.created_at,
        updated_at=record.updated_at,
        manuscript_id=record.manuscript_id,
        isbn=record.isbn,
        release_date=record.release_date,
        print_status=record.print_status,
        ebook_status=record.ebook_status,
        audiobook_status=record.audiobook_status,
        cover_status=record.cover_status,
        layout_status=record.layout_status,
        prepress_status=record.prepress_status,
        notes=record.notes,
        manuscript_title=manuscript.title,
        manuscript_status=manuscript.status,
        author_name=manuscript.author.full_name if manuscript.author else None,
    )


@router.get("", response_model=Page[ProductionRecordDetail])
def list_records(
    session: Session = Depends(get_session),
    params: PageParams = Depends(page_params),
    manuscript_id: Optional[str] = Query(default=None),
    has_release_date: Optional[bool] = Query(default=None),
    release_from: Optional[date] = Query(default=None),
    release_to: Optional[date] = Query(default=None),
) -> Page[ProductionRecordDetail]:
    stmt = select(ProductionRecord).options(
        selectinload(ProductionRecord.manuscript).selectinload(Manuscript.author)
    )
    if manuscript_id is not None:
        stmt = stmt.where(ProductionRecord.manuscript_id == manuscript_id)
    if has_release_date is True:
        stmt = stmt.where(ProductionRecord.release_date.is_not(None))
    if has_release_date is False:
        stmt = stmt.where(ProductionRecord.release_date.is_(None))
    if release_from is not None:
        stmt = stmt.where(ProductionRecord.release_date >= release_from)
    if release_to is not None:
        stmt = stmt.where(ProductionRecord.release_date <= release_to)

    # Soonest release first, then unscheduled records.
    stmt = stmt.order_by(
        ProductionRecord.release_date.is_(None),
        ProductionRecord.release_date.asc(),
        ProductionRecord.created_at.desc(),
    )

    records, total = paginate(session, stmt, params)
    return Page[ProductionRecordDetail](
        items=[_detail(r) for r in records],
        total=total,
        skip=params.skip,
        limit=params.limit,
    )


@router.get("/by-manuscript/{manuscript_id}", response_model=ProductionRecordRead)
def get_by_manuscript(
    manuscript_id: str, session: Session = Depends(get_session)
) -> ProductionRecord:
    record = session.exec(
        select(ProductionRecord).where(
            ProductionRecord.manuscript_id == manuscript_id
        )
    ).first()
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ProductionRecord not found",
        )
    return record


@router.get("/{record_id}", response_model=ProductionRecordRead)
def get_record(
    record_id: str, session: Session = Depends(get_session)
) -> ProductionRecord:
    return get_or_404(session, ProductionRecord, record_id, name="ProductionRecord")


@router.post(
    "",
    response_model=ProductionRecordRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=AUTHED,
)
def create_record(
    payload: ProductionRecordCreate, session: Session = Depends(get_session)
) -> ProductionRecord:
    ensure_exists(session, Manuscript, payload.manuscript_id, name="Manuscript")
    existing = session.exec(
        select(ProductionRecord).where(
            ProductionRecord.manuscript_id == payload.manuscript_id
        )
    ).first()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A production record already exists for this manuscript.",
        )
    record = ProductionRecord(**payload.model_dump())
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


@router.patch(
    "/{record_id}",
    response_model=ProductionRecordRead,
    dependencies=AUTHED,
)
def update_record(
    record_id: str,
    payload: ProductionRecordUpdate,
    session: Session = Depends(get_session),
) -> ProductionRecord:
    record = get_or_404(session, ProductionRecord, record_id, name="ProductionRecord")
    apply_patch(record, payload)
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


@router.delete(
    "/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=ADMIN_ONLY,
)
def delete_record(record_id: str, session: Session = Depends(get_session)):
    record = get_or_404(session, ProductionRecord, record_id, name="ProductionRecord")
    session.delete(record)
    session.commit()

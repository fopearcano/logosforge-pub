from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session, select

from app.auth import ADMIN_ONLY, AUTHED
from app.db import get_session
from app.models import Manuscript, ProductionItem, User
from app.models.enums import ProductionItemStatus, ProductionStage
from app.schemas import ProductionItemCreate, ProductionItemRead, ProductionItemUpdate
from app.utils import (
    Page,
    PageParams,
    apply_patch,
    ensure_exists,
    get_or_404,
    page_params,
    paginate,
)

router = APIRouter(prefix="/production-items", tags=["production_items"])


@router.get("", response_model=Page[ProductionItemRead])
def list_production_items(
    session: Session = Depends(get_session),
    params: PageParams = Depends(page_params),
    manuscript_id: Optional[str] = Query(default=None),
    assignee_id: Optional[str] = Query(default=None),
    stage: Optional[ProductionStage] = Query(default=None),
    status_: Optional[ProductionItemStatus] = Query(default=None, alias="status"),
) -> Page[ProductionItemRead]:
    stmt = select(ProductionItem)
    if manuscript_id is not None:
        stmt = stmt.where(ProductionItem.manuscript_id == manuscript_id)
    if assignee_id is not None:
        stmt = stmt.where(ProductionItem.assignee_id == assignee_id)
    if stage is not None:
        stmt = stmt.where(ProductionItem.stage == stage)
    if status_ is not None:
        stmt = stmt.where(ProductionItem.status == status_)
    stmt = stmt.order_by(ProductionItem.created_at.desc())

    items, total = paginate(session, stmt, params)
    return Page[ProductionItemRead](
        items=[ProductionItemRead.model_validate(i) for i in items],
        total=total,
        skip=params.skip,
        limit=params.limit,
    )


@router.get("/{item_id}", response_model=ProductionItemRead)
def get_production_item(
    item_id: str, session: Session = Depends(get_session)
) -> ProductionItem:
    return get_or_404(session, ProductionItem, item_id, name="ProductionItem")


@router.post(
    "",
    response_model=ProductionItemRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=AUTHED,
)
def create_production_item(
    payload: ProductionItemCreate, session: Session = Depends(get_session)
) -> ProductionItem:
    ensure_exists(session, Manuscript, payload.manuscript_id, name="Manuscript")
    if payload.assignee_id is not None:
        ensure_exists(session, User, payload.assignee_id, name="User")
    item = ProductionItem(**payload.model_dump())
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.patch("/{item_id}", response_model=ProductionItemRead, dependencies=AUTHED)
def update_production_item(
    item_id: str,
    payload: ProductionItemUpdate,
    session: Session = Depends(get_session),
) -> ProductionItem:
    item = get_or_404(session, ProductionItem, item_id, name="ProductionItem")
    if payload.assignee_id is not None:
        ensure_exists(session, User, payload.assignee_id, name="User")
    apply_patch(item, payload)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=ADMIN_ONLY,
)
def delete_production_item(
    item_id: str, session: Session = Depends(get_session)
):
    item = get_or_404(session, ProductionItem, item_id, name="ProductionItem")
    session.delete(item)
    session.commit()

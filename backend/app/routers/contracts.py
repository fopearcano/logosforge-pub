from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session, select

from app.db import get_session
from app.models import Author, Contract, Manuscript
from app.models.enums import ContractStatus
from app.schemas import ContractCreate, ContractRead, ContractUpdate
from app.utils import (
    Page,
    PageParams,
    apply_patch,
    ensure_exists,
    get_or_404,
    page_params,
    paginate,
)

router = APIRouter(prefix="/contracts", tags=["contracts"])


@router.get("", response_model=Page[ContractRead])
def list_contracts(
    session: Session = Depends(get_session),
    params: PageParams = Depends(page_params),
    manuscript_id: Optional[str] = Query(default=None),
    author_id: Optional[str] = Query(default=None),
    status_: Optional[ContractStatus] = Query(default=None, alias="status"),
) -> Page[ContractRead]:
    stmt = select(Contract)
    if manuscript_id is not None:
        stmt = stmt.where(Contract.manuscript_id == manuscript_id)
    if author_id is not None:
        stmt = stmt.where(Contract.author_id == author_id)
    if status_ is not None:
        stmt = stmt.where(Contract.status == status_)
    stmt = stmt.order_by(Contract.created_at.desc())

    items, total = paginate(session, stmt, params)
    return Page[ContractRead](
        items=[ContractRead.model_validate(i) for i in items],
        total=total,
        skip=params.skip,
        limit=params.limit,
    )


@router.get("/{contract_id}", response_model=ContractRead)
def get_contract(contract_id: str, session: Session = Depends(get_session)) -> Contract:
    return get_or_404(session, Contract, contract_id, name="Contract")


@router.post("", response_model=ContractRead, status_code=status.HTTP_201_CREATED)
def create_contract(
    payload: ContractCreate, session: Session = Depends(get_session)
) -> Contract:
    ensure_exists(session, Manuscript, payload.manuscript_id, name="Manuscript")
    ensure_exists(session, Author, payload.author_id, name="Author")
    contract = Contract(**payload.model_dump())
    session.add(contract)
    session.commit()
    session.refresh(contract)
    return contract


@router.patch("/{contract_id}", response_model=ContractRead)
def update_contract(
    contract_id: str,
    payload: ContractUpdate,
    session: Session = Depends(get_session),
) -> Contract:
    contract = get_or_404(session, Contract, contract_id, name="Contract")
    apply_patch(contract, payload)
    session.add(contract)
    session.commit()
    session.refresh(contract)
    return contract


@router.delete("/{contract_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contract(contract_id: str, session: Session = Depends(get_session)):
    contract = get_or_404(session, Contract, contract_id, name="Contract")
    session.delete(contract)
    session.commit()

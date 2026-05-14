from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.auth import ADMIN_ONLY, AUTHED
from app.db import get_session
from app.models import (
    KnowledgeEntity,
    KnowledgeRelationship,
    Manuscript,
    ManuscriptEntityLink,
)
from app.models.enums import (
    EntityKind,
    ManuscriptLinkRole,
    RelationshipKind,
)
from app.schemas import (
    KnowledgeEntityCreate,
    KnowledgeEntityRead,
    KnowledgeEntityUpdate,
    KnowledgeRelationshipCreate,
    KnowledgeRelationshipDetail,
    KnowledgeRelationshipRead,
    KnowledgeRelationshipUpdate,
    ManuscriptEntityLinkCreate,
    ManuscriptEntityLinkRead,
    ManuscriptEntityLinkUpdate,
    NeighborhoodResult,
)
from app.services.knowledge import neighborhood, slugify
from app.utils import (
    Page,
    PageParams,
    apply_patch,
    ensure_exists,
    get_or_404,
    page_params,
    paginate,
)

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


# --- helpers --------------------------------------------------------------


def _relationship_detail(rel: KnowledgeRelationship) -> KnowledgeRelationshipDetail:
    src = rel.source
    tgt = rel.target
    return KnowledgeRelationshipDetail(
        id=rel.id,
        created_at=rel.created_at,
        updated_at=rel.updated_at,
        source_id=rel.source_id,
        target_id=rel.target_id,
        kind=rel.kind,
        weight=rel.weight,
        description=rel.description,
        source_name=src.name if src else None,
        source_kind=src.kind if src else None,
        target_name=tgt.name if tgt else None,
        target_kind=tgt.kind if tgt else None,
    )


def _link_read(link: ManuscriptEntityLink) -> ManuscriptEntityLinkRead:
    entity = link.entity
    return ManuscriptEntityLinkRead(
        id=link.id,
        created_at=link.created_at,
        updated_at=link.updated_at,
        manuscript_id=link.manuscript_id,
        entity_id=link.entity_id,
        role=link.role,
        relevance=link.relevance,
        notes=link.notes,
        entity_name=entity.name if entity else None,
        entity_kind=entity.kind if entity else None,
        entity_slug=entity.slug if entity else None,
    )


def _resolve_slug(session: Session, name: str, provided: Optional[str]) -> str:
    """Return a slug that's free in the entities table.

    If ``provided`` is given, validate uniqueness. Otherwise derive from
    ``name`` and append ``-2``, ``-3`` … until we find an unused form.
    """
    candidate = (provided or slugify(name)).strip().lower()
    if not candidate:
        candidate = "entity"
    if provided:
        # Caller is asserting this exact slug; let an IntegrityError
        # surface a 409 if it clashes.
        return candidate

    base = candidate
    suffix = 2
    while session.exec(
        select(KnowledgeEntity.id).where(KnowledgeEntity.slug == candidate)
    ).first() is not None:
        candidate = f"{base}-{suffix}"
        suffix += 1
    return candidate


# --- entities -------------------------------------------------------------


@router.get("/entities", response_model=Page[KnowledgeEntityRead])
def list_entities(
    session: Session = Depends(get_session),
    params: PageParams = Depends(page_params),
    kind: Optional[EntityKind] = Query(default=None),
    q: Optional[str] = Query(
        default=None, description="Substring match on name (case-insensitive)"
    ),
) -> Page[KnowledgeEntityRead]:
    stmt = select(KnowledgeEntity)
    if kind is not None:
        stmt = stmt.where(KnowledgeEntity.kind == kind)
    if q:
        stmt = stmt.where(KnowledgeEntity.name.ilike(f"%{q}%"))
    stmt = stmt.order_by(KnowledgeEntity.kind, KnowledgeEntity.name)

    items, total = paginate(session, stmt, params)
    return Page[KnowledgeEntityRead](
        items=[KnowledgeEntityRead.model_validate(e) for e in items],
        total=total,
        skip=params.skip,
        limit=params.limit,
    )


@router.get("/entities/{entity_id}", response_model=KnowledgeEntityRead)
def get_entity(
    entity_id: str, session: Session = Depends(get_session)
) -> KnowledgeEntity:
    return get_or_404(session, KnowledgeEntity, entity_id, name="KnowledgeEntity")


@router.get("/entities/by-slug/{slug}", response_model=KnowledgeEntityRead)
def get_entity_by_slug(
    slug: str, session: Session = Depends(get_session)
) -> KnowledgeEntity:
    entity = session.exec(
        select(KnowledgeEntity).where(KnowledgeEntity.slug == slug)
    ).first()
    if entity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KnowledgeEntity not found",
        )
    return entity


@router.post(
    "/entities",
    response_model=KnowledgeEntityRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=AUTHED,
)
def create_entity(
    payload: KnowledgeEntityCreate, session: Session = Depends(get_session)
) -> KnowledgeEntity:
    slug = _resolve_slug(session, payload.name, payload.slug)
    entity = KnowledgeEntity(
        name=payload.name.strip(),
        slug=slug,
        kind=payload.kind,
        description=payload.description,
        extras=payload.extras,
    )
    session.add(entity)
    session.commit()
    session.refresh(entity)
    return entity


@router.patch(
    "/entities/{entity_id}",
    response_model=KnowledgeEntityRead,
    dependencies=AUTHED,
)
def update_entity(
    entity_id: str,
    payload: KnowledgeEntityUpdate,
    session: Session = Depends(get_session),
) -> KnowledgeEntity:
    entity = get_or_404(
        session, KnowledgeEntity, entity_id, name="KnowledgeEntity"
    )
    apply_patch(entity, payload)
    session.add(entity)
    session.commit()
    session.refresh(entity)
    return entity


@router.delete(
    "/entities/{entity_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=ADMIN_ONLY,
)
def delete_entity(
    entity_id: str, session: Session = Depends(get_session)
):
    entity = get_or_404(
        session, KnowledgeEntity, entity_id, name="KnowledgeEntity"
    )
    # Cascade in app code so the API behaves predictably on every backend.
    relationships = list(
        session.exec(
            select(KnowledgeRelationship).where(
                or_(
                    KnowledgeRelationship.source_id == entity_id,
                    KnowledgeRelationship.target_id == entity_id,
                )
            )
        ).all()
    )
    for rel in relationships:
        session.delete(rel)
    links = list(
        session.exec(
            select(ManuscriptEntityLink).where(
                ManuscriptEntityLink.entity_id == entity_id
            )
        ).all()
    )
    for link in links:
        session.delete(link)
    session.delete(entity)
    session.commit()


@router.get(
    "/entities/{entity_id}/neighborhood",
    response_model=NeighborhoodResult,
)
def entity_neighborhood(
    entity_id: str,
    session: Session = Depends(get_session),
    depth: int = Query(default=1, ge=1, le=4),
    limit: int = Query(default=200, ge=1, le=500),
) -> NeighborhoodResult:
    result = neighborhood(session, entity_id, depth=depth, limit=limit)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KnowledgeEntity not found",
        )
    return result


@router.get(
    "/entities/{entity_id}/manuscripts",
    response_model=list[ManuscriptEntityLinkRead],
    summary="List manuscripts linked to this entity",
)
def entity_manuscripts(
    entity_id: str, session: Session = Depends(get_session)
) -> list[ManuscriptEntityLinkRead]:
    ensure_exists(session, KnowledgeEntity, entity_id, name="KnowledgeEntity")
    rows = list(
        session.exec(
            select(ManuscriptEntityLink)
            .where(ManuscriptEntityLink.entity_id == entity_id)
            .options(selectinload(ManuscriptEntityLink.entity))
            .order_by(ManuscriptEntityLink.created_at.desc())
        ).all()
    )
    return [_link_read(r) for r in rows]


# --- relationships --------------------------------------------------------


@router.get(
    "/relationships",
    response_model=Page[KnowledgeRelationshipDetail],
)
def list_relationships(
    session: Session = Depends(get_session),
    params: PageParams = Depends(page_params),
    source_id: Optional[str] = Query(default=None),
    target_id: Optional[str] = Query(default=None),
    kind: Optional[RelationshipKind] = Query(default=None),
) -> Page[KnowledgeRelationshipDetail]:
    stmt = select(KnowledgeRelationship).options(
        selectinload(KnowledgeRelationship.source),
        selectinload(KnowledgeRelationship.target),
    )
    if source_id is not None:
        stmt = stmt.where(KnowledgeRelationship.source_id == source_id)
    if target_id is not None:
        stmt = stmt.where(KnowledgeRelationship.target_id == target_id)
    if kind is not None:
        stmt = stmt.where(KnowledgeRelationship.kind == kind)
    stmt = stmt.order_by(KnowledgeRelationship.created_at.desc())

    rows, total = paginate(session, stmt, params)
    return Page[KnowledgeRelationshipDetail](
        items=[_relationship_detail(r) for r in rows],
        total=total,
        skip=params.skip,
        limit=params.limit,
    )


@router.get(
    "/relationships/{rel_id}",
    response_model=KnowledgeRelationshipDetail,
)
def get_relationship(
    rel_id: str, session: Session = Depends(get_session)
) -> KnowledgeRelationshipDetail:
    rel = get_or_404(
        session, KnowledgeRelationship, rel_id, name="KnowledgeRelationship"
    )
    # Touch the relationships so the detail builder can read the names.
    _ = rel.source
    _ = rel.target
    return _relationship_detail(rel)


@router.post(
    "/relationships",
    response_model=KnowledgeRelationshipRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=AUTHED,
)
def create_relationship(
    payload: KnowledgeRelationshipCreate,
    session: Session = Depends(get_session),
) -> KnowledgeRelationship:
    if payload.source_id == payload.target_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An entity cannot relate to itself.",
        )
    ensure_exists(
        session, KnowledgeEntity, payload.source_id, name="source entity"
    )
    ensure_exists(
        session, KnowledgeEntity, payload.target_id, name="target entity"
    )
    rel = KnowledgeRelationship(**payload.model_dump())
    session.add(rel)
    session.commit()
    session.refresh(rel)
    return rel


@router.patch(
    "/relationships/{rel_id}",
    response_model=KnowledgeRelationshipRead,
    dependencies=AUTHED,
)
def update_relationship(
    rel_id: str,
    payload: KnowledgeRelationshipUpdate,
    session: Session = Depends(get_session),
) -> KnowledgeRelationship:
    rel = get_or_404(
        session, KnowledgeRelationship, rel_id, name="KnowledgeRelationship"
    )
    apply_patch(rel, payload)
    session.add(rel)
    session.commit()
    session.refresh(rel)
    return rel


@router.delete(
    "/relationships/{rel_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=AUTHED,
)
def delete_relationship(
    rel_id: str, session: Session = Depends(get_session)
):
    rel = get_or_404(
        session, KnowledgeRelationship, rel_id, name="KnowledgeRelationship"
    )
    session.delete(rel)
    session.commit()


# --- manuscript-scoped links ---------------------------------------------


manuscript_links_router = APIRouter(tags=["knowledge"])


@manuscript_links_router.get(
    "/manuscripts/{manuscript_id}/entity-links",
    response_model=list[ManuscriptEntityLinkRead],
)
def list_manuscript_links(
    manuscript_id: str,
    session: Session = Depends(get_session),
    role: Optional[ManuscriptLinkRole] = Query(default=None),
) -> list[ManuscriptEntityLinkRead]:
    ensure_exists(session, Manuscript, manuscript_id, name="Manuscript")
    stmt = (
        select(ManuscriptEntityLink)
        .where(ManuscriptEntityLink.manuscript_id == manuscript_id)
        .options(selectinload(ManuscriptEntityLink.entity))
        .order_by(ManuscriptEntityLink.role, ManuscriptEntityLink.created_at.desc())
    )
    if role is not None:
        stmt = stmt.where(ManuscriptEntityLink.role == role)
    rows = list(session.exec(stmt).all())
    return [_link_read(r) for r in rows]


@manuscript_links_router.post(
    "/manuscripts/{manuscript_id}/entity-links",
    response_model=ManuscriptEntityLinkRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=AUTHED,
)
def create_manuscript_link(
    manuscript_id: str,
    payload: ManuscriptEntityLinkCreate,
    session: Session = Depends(get_session),
) -> ManuscriptEntityLinkRead:
    # Permit the URL manuscript_id to override the body for convenience.
    if payload.manuscript_id != manuscript_id:
        payload = payload.model_copy(update={"manuscript_id": manuscript_id})

    ensure_exists(session, Manuscript, payload.manuscript_id, name="Manuscript")
    ensure_exists(
        session, KnowledgeEntity, payload.entity_id, name="KnowledgeEntity"
    )
    link = ManuscriptEntityLink(**payload.model_dump())
    session.add(link)
    session.commit()
    session.refresh(link)
    return _link_read(link)


@manuscript_links_router.patch(
    "/manuscripts/{manuscript_id}/entity-links/{link_id}",
    response_model=ManuscriptEntityLinkRead,
    dependencies=AUTHED,
)
def update_manuscript_link(
    manuscript_id: str,
    link_id: str,
    payload: ManuscriptEntityLinkUpdate,
    session: Session = Depends(get_session),
) -> ManuscriptEntityLinkRead:
    link = get_or_404(
        session, ManuscriptEntityLink, link_id, name="ManuscriptEntityLink"
    )
    if link.manuscript_id != manuscript_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ManuscriptEntityLink not found",
        )
    apply_patch(link, payload)
    session.add(link)
    session.commit()
    session.refresh(link)
    return _link_read(link)


@manuscript_links_router.delete(
    "/manuscripts/{manuscript_id}/entity-links/{link_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=AUTHED,
)
def delete_manuscript_link(
    manuscript_id: str,
    link_id: str,
    session: Session = Depends(get_session),
):
    link = get_or_404(
        session, ManuscriptEntityLink, link_id, name="ManuscriptEntityLink"
    )
    if link.manuscript_id != manuscript_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ManuscriptEntityLink not found",
        )
    session.delete(link)
    session.commit()

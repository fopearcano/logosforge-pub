"""Graph helpers for the editorial knowledge layer.

* ``slugify`` produces stable, URL-safe identifiers for entities.
* ``neighborhood`` does a breadth-first walk of typed edges so the
  router can return a graph fragment without leaking ORM internals.
"""
from __future__ import annotations

import re
from typing import Optional

from sqlalchemy import or_
from sqlmodel import Session, select

from app.models import KnowledgeEntity, KnowledgeRelationship
from app.schemas.knowledge import (
    NeighborhoodEdge,
    NeighborhoodNode,
    NeighborhoodResult,
)


_SLUG_PATTERN = re.compile(r"[^a-z0-9]+")


def slugify(value: str) -> str:
    """Lower-case, hyphen-joined, alphanumeric-only.

    A safety net only — callers may pass an explicit slug to escape
    a collision.
    """
    slug = _SLUG_PATTERN.sub("-", value.lower()).strip("-")
    return slug or "entity"


def neighborhood(
    session: Session,
    root_id: str,
    *,
    depth: int = 1,
    limit: int = 200,
) -> Optional[NeighborhoodResult]:
    """BFS outward from ``root_id`` up to ``depth`` hops.

    Returns ``None`` if the root entity does not exist. Stops adding
    nodes once the total reaches ``limit`` — the typed edges already
    discovered are still returned so the partial graph is coherent.
    """
    root = session.get(KnowledgeEntity, root_id)
    if root is None:
        return None

    nodes: dict[str, tuple[KnowledgeEntity, int]] = {root.id: (root, 0)}
    edges: dict[str, KnowledgeRelationship] = {}
    frontier: set[str] = {root.id}

    for hop in range(depth):
        if not frontier:
            break

        relations = list(
            session.exec(
                select(KnowledgeRelationship).where(
                    or_(
                        KnowledgeRelationship.source_id.in_(frontier),
                        KnowledgeRelationship.target_id.in_(frontier),
                    )
                )
            ).all()
        )

        next_frontier: set[str] = set()
        for rel in relations:
            edges.setdefault(rel.id, rel)
            for other_id in (rel.source_id, rel.target_id):
                if other_id not in nodes:
                    next_frontier.add(other_id)

        if not next_frontier:
            break

        # Cap nodes at the configured limit (root already counts).
        room = max(0, limit - len(nodes))
        new_ids = list(next_frontier)[:room]
        if new_ids:
            fetched = list(
                session.exec(
                    select(KnowledgeEntity).where(
                        KnowledgeEntity.id.in_(new_ids)
                    )
                ).all()
            )
            for entity in fetched:
                nodes[entity.id] = (entity, hop + 1)

        frontier = set(new_ids)
        if len(nodes) >= limit:
            break

    node_list = [
        NeighborhoodNode(
            id=entity.id,
            name=entity.name,
            slug=entity.slug,
            kind=entity.kind,
            distance=distance,
        )
        for entity, distance in nodes.values()
    ]
    edge_list = [
        NeighborhoodEdge(
            id=rel.id,
            source_id=rel.source_id,
            target_id=rel.target_id,
            kind=rel.kind,
            weight=rel.weight,
            description=rel.description,
        )
        # Only keep edges whose endpoints both made it into the result.
        for rel in edges.values()
        if rel.source_id in nodes and rel.target_id in nodes
    ]

    return NeighborhoodResult(
        root_id=root.id,
        depth=depth,
        nodes=node_list,
        edges=edge_list,
    )

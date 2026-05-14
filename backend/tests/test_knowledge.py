"""Knowledge-graph endpoint and traversal tests."""
from __future__ import annotations

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models import (
    Author,
    KnowledgeEntity,
    KnowledgeRelationship,
    Manuscript,
    ManuscriptEntityLink,
)
from app.models.enums import (
    EntityKind,
    ManuscriptLinkRole,
    RelationshipKind,
    WorkflowStatus,
)


# --- helpers -------------------------------------------------------------


def _author_and_manuscript(session: Session) -> Manuscript:
    a = Author(full_name="K Author")
    session.add(a)
    session.commit()
    session.refresh(a)
    m = Manuscript(
        title="K Manuscript", author_id=a.id, status=WorkflowStatus.ACCEPTED
    )
    session.add(m)
    session.commit()
    session.refresh(m)
    return m


def _seed_chain(session: Session) -> dict[str, KnowledgeEntity]:
    a = KnowledgeEntity(name="Alpha", slug="alpha", kind=EntityKind.THEME)
    b = KnowledgeEntity(name="Beta", slug="beta", kind=EntityKind.MOTIF)
    c = KnowledgeEntity(name="Gamma", slug="gamma", kind=EntityKind.PERSON)
    d = KnowledgeEntity(name="Delta", slug="delta", kind=EntityKind.PLACE)
    session.add_all([a, b, c, d])
    session.commit()
    for e in (a, b, c, d):
        session.refresh(e)

    session.add_all(
        [
            KnowledgeRelationship(
                source_id=a.id, target_id=b.id, kind=RelationshipKind.RELATED_TO
            ),
            KnowledgeRelationship(
                source_id=b.id, target_id=c.id, kind=RelationshipKind.INFLUENCES
            ),
            KnowledgeRelationship(
                source_id=c.id, target_id=d.id, kind=RelationshipKind.PART_OF
            ),
        ]
    )
    session.commit()
    return {"a": a, "b": b, "c": c, "d": d}


# --- entity CRUD ---------------------------------------------------------


def test_create_entity_derives_slug(client: TestClient) -> None:
    r = client.post(
        "/api/knowledge/entities",
        json={"name": "Inland Seas", "kind": "theme"},
    )
    assert r.status_code == 201
    body = r.json()
    assert body["slug"] == "inland-seas"
    assert body["kind"] == "theme"


def test_create_entity_with_explicit_slug(client: TestClient) -> None:
    r = client.post(
        "/api/knowledge/entities",
        json={"name": "Display Name", "slug": "custom-handle", "kind": "motif"},
    )
    assert r.status_code == 201
    assert r.json()["slug"] == "custom-handle"


def test_duplicate_derived_slug_is_disambiguated(
    client: TestClient,
) -> None:
    # First create derives "memory"; the second should land on "memory-2".
    a = client.post(
        "/api/knowledge/entities", json={"name": "Memory", "kind": "theme"}
    ).json()
    b = client.post(
        "/api/knowledge/entities", json={"name": "Memory", "kind": "theme"}
    ).json()
    assert a["slug"] == "memory"
    assert b["slug"] == "memory-2"


def test_duplicate_explicit_slug_returns_409(client: TestClient) -> None:
    client.post(
        "/api/knowledge/entities",
        json={"name": "First", "slug": "shared", "kind": "theme"},
    )
    r = client.post(
        "/api/knowledge/entities",
        json={"name": "Second", "slug": "shared", "kind": "theme"},
    )
    assert r.status_code == 409


def test_entity_create_requires_auth(anon_client: TestClient) -> None:
    r = anon_client.post(
        "/api/knowledge/entities",
        json={"name": "X", "kind": "theme"},
    )
    assert r.status_code == 401


def test_get_entity_by_slug(client: TestClient) -> None:
    client.post(
        "/api/knowledge/entities",
        json={"name": "Salt", "kind": "motif"},
    )
    body = client.get("/api/knowledge/entities/by-slug/salt").json()
    assert body["name"] == "Salt"


def test_list_entities_filters_by_kind_and_query(client: TestClient) -> None:
    client.post(
        "/api/knowledge/entities", json={"name": "Memory", "kind": "theme"}
    )
    client.post(
        "/api/knowledge/entities", json={"name": "Salt", "kind": "motif"}
    )
    client.post(
        "/api/knowledge/entities", json={"name": "Saltwater", "kind": "motif"}
    )

    themes = client.get("/api/knowledge/entities?kind=theme").json()
    assert themes["total"] == 1
    assert themes["items"][0]["name"] == "Memory"

    search = client.get("/api/knowledge/entities?q=salt").json()
    assert search["total"] == 2


# --- relationships -------------------------------------------------------


def test_create_relationship_links_entities(
    client: TestClient, session: Session
) -> None:
    es = _seed_chain(session)
    r = client.post(
        "/api/knowledge/relationships",
        json={
            "source_id": es["a"].id,
            "target_id": es["d"].id,
            "kind": "related_to",
            "weight": 0.5,
        },
    )
    assert r.status_code == 201
    detail = client.get(f"/api/knowledge/relationships/{r.json()['id']}").json()
    assert detail["source_name"] == "Alpha"
    assert detail["target_name"] == "Delta"
    assert detail["kind"] == "related_to"


def test_relationship_rejects_self_loop(
    client: TestClient, session: Session
) -> None:
    es = _seed_chain(session)
    r = client.post(
        "/api/knowledge/relationships",
        json={
            "source_id": es["a"].id,
            "target_id": es["a"].id,
            "kind": "related_to",
        },
    )
    assert r.status_code == 409


def test_relationship_requires_existing_endpoints(client: TestClient) -> None:
    e = client.post(
        "/api/knowledge/entities",
        json={"name": "Sole", "kind": "theme"},
    ).json()
    r = client.post(
        "/api/knowledge/relationships",
        json={
            "source_id": e["id"],
            "target_id": "no-such-id",
            "kind": "related_to",
        },
    )
    assert r.status_code == 404


def test_list_relationships_filters_by_endpoint(
    client: TestClient, session: Session
) -> None:
    es = _seed_chain(session)
    body = client.get(
        f"/api/knowledge/relationships?source_id={es['b'].id}"
    ).json()
    assert body["total"] == 1
    assert body["items"][0]["source_id"] == es["b"].id


# --- neighborhood --------------------------------------------------------


def test_neighborhood_one_hop(
    anon_client: TestClient, session: Session
) -> None:
    es = _seed_chain(session)
    body = anon_client.get(
        f"/api/knowledge/entities/{es['b'].id}/neighborhood?depth=1"
    ).json()
    assert body["root_id"] == es["b"].id
    distances = {n["id"]: n["distance"] for n in body["nodes"]}
    assert distances[es["b"].id] == 0
    assert distances[es["a"].id] == 1
    assert distances[es["c"].id] == 1
    # Delta is two hops away, not included.
    assert es["d"].id not in distances


def test_neighborhood_two_hops(
    anon_client: TestClient, session: Session
) -> None:
    es = _seed_chain(session)
    body = anon_client.get(
        f"/api/knowledge/entities/{es['a'].id}/neighborhood?depth=2"
    ).json()
    ids = {n["id"] for n in body["nodes"]}
    # From Alpha, depth 2 reaches Beta and Gamma but not Delta.
    assert es["a"].id in ids
    assert es["b"].id in ids
    assert es["c"].id in ids
    assert es["d"].id not in ids
    # Two edges should accompany the three reachable nodes.
    assert len(body["edges"]) == 2


def test_neighborhood_404_for_missing_root(anon_client: TestClient) -> None:
    r = anon_client.get("/api/knowledge/entities/no-such/neighborhood")
    assert r.status_code == 404


# --- cascade delete ------------------------------------------------------


def test_delete_entity_clears_relationships_and_links(
    client: TestClient, session: Session
) -> None:
    es = _seed_chain(session)
    manuscript = _author_and_manuscript(session)
    session.add(
        ManuscriptEntityLink(
            manuscript_id=manuscript.id, entity_id=es["b"].id
        )
    )
    session.commit()

    r = client.delete(f"/api/knowledge/entities/{es['b'].id}")
    assert r.status_code == 204
    # Entity gone.
    assert client.get(f"/api/knowledge/entities/{es['b'].id}").status_code == 404
    # Relationships touching Beta gone.
    assert (
        client.get(
            f"/api/knowledge/relationships?source_id={es['b'].id}"
        ).json()["total"]
        == 0
    )
    assert (
        client.get(
            f"/api/knowledge/relationships?target_id={es['b'].id}"
        ).json()["total"]
        == 0
    )
    # Manuscript-side link gone.
    assert (
        client.get(
            f"/api/manuscripts/{manuscript.id}/entity-links"
        ).json()
        == []
    )


def test_delete_entity_requires_admin(
    editor_client: TestClient, client: TestClient, session: Session
) -> None:
    es = _seed_chain(session)
    refused = editor_client.delete(f"/api/knowledge/entities/{es['a'].id}")
    assert refused.status_code == 403


# --- manuscript links ---------------------------------------------------


def test_manuscript_entity_link_lifecycle(
    client: TestClient, session: Session
) -> None:
    manuscript = _author_and_manuscript(session)
    entity = client.post(
        "/api/knowledge/entities",
        json={"name": "Theme One", "kind": "theme"},
    ).json()

    created = client.post(
        f"/api/manuscripts/{manuscript.id}/entity-links",
        json={
            "manuscript_id": manuscript.id,
            "entity_id": entity["id"],
            "role": "tagged",
            "relevance": 0.8,
        },
    )
    assert created.status_code == 201
    body = created.json()
    assert body["entity_name"] == "Theme One"
    assert body["entity_kind"] == "theme"
    assert body["entity_slug"] == "theme-one"

    listed = client.get(
        f"/api/manuscripts/{manuscript.id}/entity-links"
    ).json()
    assert len(listed) == 1
    link_id = listed[0]["id"]

    patched = client.patch(
        f"/api/manuscripts/{manuscript.id}/entity-links/{link_id}",
        json={"role": "features", "relevance": 0.9},
    ).json()
    assert patched["role"] == "features"
    assert patched["relevance"] == 0.9

    deleted = client.delete(
        f"/api/manuscripts/{manuscript.id}/entity-links/{link_id}"
    )
    assert deleted.status_code == 204
    assert client.get(
        f"/api/manuscripts/{manuscript.id}/entity-links"
    ).json() == []


def test_manuscript_link_create_requires_existing_endpoints(
    client: TestClient, session: Session
) -> None:
    manuscript = _author_and_manuscript(session)
    r = client.post(
        f"/api/manuscripts/{manuscript.id}/entity-links",
        json={
            "manuscript_id": manuscript.id,
            "entity_id": "no-such",
            "role": "tagged",
        },
    )
    assert r.status_code == 404


def test_manuscript_link_create_requires_auth(
    anon_client: TestClient, session: Session
) -> None:
    manuscript = _author_and_manuscript(session)
    r = anon_client.post(
        f"/api/manuscripts/{manuscript.id}/entity-links",
        json={
            "manuscript_id": manuscript.id,
            "entity_id": "any",
            "role": "tagged",
        },
    )
    assert r.status_code == 401


def test_manuscript_link_filters_by_role(
    client: TestClient, session: Session
) -> None:
    manuscript = _author_and_manuscript(session)
    tag = client.post(
        "/api/knowledge/entities",
        json={"name": "Tagged Entity", "kind": "theme"},
    ).json()
    place = client.post(
        "/api/knowledge/entities",
        json={"name": "Place Entity", "kind": "place"},
    ).json()
    client.post(
        f"/api/manuscripts/{manuscript.id}/entity-links",
        json={
            "manuscript_id": manuscript.id,
            "entity_id": tag["id"],
            "role": "tagged",
        },
    )
    client.post(
        f"/api/manuscripts/{manuscript.id}/entity-links",
        json={
            "manuscript_id": manuscript.id,
            "entity_id": place["id"],
            "role": "set_in",
        },
    )

    tagged = client.get(
        f"/api/manuscripts/{manuscript.id}/entity-links?role=tagged"
    ).json()
    assert len(tagged) == 1
    assert tagged[0]["entity_kind"] == "theme"


def test_entity_manuscripts_endpoint(
    client: TestClient, session: Session
) -> None:
    manuscript = _author_and_manuscript(session)
    entity = client.post(
        "/api/knowledge/entities",
        json={"name": "Subject", "kind": "theme"},
    ).json()
    client.post(
        f"/api/manuscripts/{manuscript.id}/entity-links",
        json={
            "manuscript_id": manuscript.id,
            "entity_id": entity["id"],
            "role": "tagged",
        },
    )
    body = client.get(
        f"/api/knowledge/entities/{entity['id']}/manuscripts"
    ).json()
    assert len(body) == 1
    assert body[0]["manuscript_id"] == manuscript.id


# --- service-level slugify ----------------------------------------------


def test_slugify_handles_punctuation_and_diacritics() -> None:
    from app.services.knowledge import slugify

    assert slugify("Inland Seas") == "inland-seas"
    assert slugify("type-design") == "type-design"
    assert slugify("Mémoire & Lettres!") == "m-moire-lettres"
    assert slugify("   ") == "entity"

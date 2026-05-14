from __future__ import annotations

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.auth.security import hash_password
from app.models import User, UserRole


def _make_user_with_password(
    session: Session,
    *,
    email: str,
    password: str,
    role: UserRole = UserRole.EDITOR,
    is_active: bool = True,
) -> User:
    user = User(
        email=email,
        full_name=email.split("@")[0],
        role=role,
        is_active=is_active,
        hashed_password=hash_password(password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def test_login_with_valid_credentials_returns_token(
    anon_client: TestClient, session: Session
) -> None:
    _make_user_with_password(
        session, email="helena@logosforge.test", password="folio", role=UserRole.ADMIN
    )

    r = anon_client.post(
        "/api/auth/login",
        data={"username": "helena@logosforge.test", "password": "folio"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["user"]["email"] == "helena@logosforge.test"
    assert body["user"]["role"] == "admin"
    assert "expires_at" in body


def test_login_with_wrong_password_returns_401(
    anon_client: TestClient, session: Session
) -> None:
    _make_user_with_password(
        session, email="x@logosforge.test", password="correct"
    )
    r = anon_client.post(
        "/api/auth/login",
        data={"username": "x@logosforge.test", "password": "wrong"},
    )
    assert r.status_code == 401
    assert r.json()["detail"] == "Invalid credentials"


def test_login_unknown_user_returns_401(anon_client: TestClient) -> None:
    r = anon_client.post(
        "/api/auth/login",
        data={"username": "ghost@logosforge.test", "password": "anything"},
    )
    assert r.status_code == 401


def test_login_inactive_user_returns_401(
    anon_client: TestClient, session: Session
) -> None:
    _make_user_with_password(
        session, email="dormant@logosforge.test", password="folio", is_active=False
    )
    r = anon_client.post(
        "/api/auth/login",
        data={"username": "dormant@logosforge.test", "password": "folio"},
    )
    assert r.status_code == 401
    assert r.json()["detail"] == "Inactive account"


def test_me_requires_authentication(anon_client: TestClient) -> None:
    r = anon_client.get("/api/auth/me")
    assert r.status_code == 401


def test_me_returns_current_user(client: TestClient) -> None:
    r = client.get("/api/auth/me")
    assert r.status_code == 200
    body = r.json()
    assert body["email"] == "admin@logosforge.test"
    assert body["role"] == "admin"


def test_protected_post_rejects_anonymous(anon_client: TestClient) -> None:
    r = anon_client.post(
        "/api/authors", json={"full_name": "Should Not Land"}
    )
    assert r.status_code == 401


def test_protected_post_with_garbage_token(anon_client: TestClient) -> None:
    anon_client.headers["Authorization"] = "Bearer not-a-real-token"
    r = anon_client.post("/api/authors", json={"full_name": "Nope"})
    assert r.status_code == 401


def test_admin_only_delete_rejects_editor(
    editor_client: TestClient, client: TestClient
) -> None:
    # Admin client creates the author...
    created = client.post(
        "/api/authors", json={"full_name": "Disposable"}
    )
    author_id = created.json()["id"]

    # ...editor cannot delete it.
    r = editor_client.delete(f"/api/authors/{author_id}")
    assert r.status_code == 403
    assert r.json()["detail"] == "Insufficient role"

    # The record is untouched.
    still_there = client.get(f"/api/authors/{author_id}")
    assert still_there.status_code == 200


def test_editor_can_create_but_not_delete(
    editor_client: TestClient, client: TestClient
) -> None:
    created = editor_client.post(
        "/api/authors", json={"full_name": "Editor's Pick"}
    )
    assert created.status_code == 201
    author_id = created.json()["id"]

    refused = editor_client.delete(f"/api/authors/{author_id}")
    assert refused.status_code == 403

    allowed = client.delete(f"/api/authors/{author_id}")
    assert allowed.status_code == 204


def test_anonymous_can_still_list(anon_client: TestClient) -> None:
    # GET endpoints remain public.
    r = anon_client.get("/api/authors")
    assert r.status_code == 200
    assert r.json()["items"] == []


def test_oauth2_scheme_advertises_correct_token_url(anon_client: TestClient) -> None:
    openapi = anon_client.get("/openapi.json").json()
    scheme = openapi["components"]["securitySchemes"]["OAuth2PasswordBearer"]
    assert scheme["type"] == "oauth2"
    assert scheme["flows"]["password"]["tokenUrl"] == "/api/auth/login"

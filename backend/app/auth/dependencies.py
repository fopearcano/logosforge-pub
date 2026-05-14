"""FastAPI dependencies for authentication and role-based access control."""
from __future__ import annotations

from collections.abc import Iterable

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from app.auth.security import decode_token
from app.config import settings
from app.db import get_session
from app.models import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.api_prefix}/auth/login",
    auto_error=True,
)


_CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
) -> User:
    try:
        payload = decode_token(token)
        subject = payload.get("sub")
        if not isinstance(subject, str):
            raise _CREDENTIALS_EXCEPTION
    except jwt.PyJWTError as exc:
        raise _CREDENTIALS_EXCEPTION from exc

    user = session.get(User, subject)
    if user is None or not user.is_active:
        raise _CREDENTIALS_EXCEPTION
    return user


def require_role(*allowed: UserRole):
    """Dependency factory that allows only callers whose role is in `allowed`."""
    allowed_set: frozenset[UserRole] = frozenset(allowed)

    def _dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed_set:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role",
            )
        return user

    return _dependency


def require_any_role(allowed: Iterable[UserRole]):
    """Variant accepting an iterable of roles. Useful for shared role tuples."""
    return require_role(*allowed)


# Reusable dependency lists for FastAPI route decorators. Define once, attach
# everywhere — avoids 21 copies of the same Depends() call across CRUD routers.
AUTHED: list = [Depends(get_current_user)]
ADMIN_ONLY: list = [Depends(require_role(UserRole.ADMIN))]

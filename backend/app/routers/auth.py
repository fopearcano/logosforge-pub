from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from app.auth.dependencies import get_current_user
from app.auth.security import create_access_token, verify_password
from app.db import get_session
from app.models import User
from app.schemas import CurrentUserRead, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse, summary="Issue an access token")
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
) -> TokenResponse:
    user = session.exec(select(User).where(User.email == form.username)).first()
    if user is None or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive account",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token, expires_at = create_access_token(subject=user.id, role=user.role.value)
    return TokenResponse(
        access_token=token,
        expires_at=expires_at,
        user=CurrentUserRead.model_validate(user),
    )


@router.get("/me", response_model=CurrentUserRead, summary="Current authenticated user")
def me(user: User = Depends(get_current_user)) -> User:
    return user

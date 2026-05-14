"""Authentication primitives: hashing, JWT, dependencies."""

from app.auth.dependencies import (
    ADMIN_ONLY,
    AUTHED,
    get_current_user,
    oauth2_scheme,
    require_role,
)
from app.auth.security import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)

__all__ = [
    "ADMIN_ONLY",
    "AUTHED",
    "create_access_token",
    "decode_token",
    "get_current_user",
    "hash_password",
    "oauth2_scheme",
    "require_role",
    "verify_password",
]

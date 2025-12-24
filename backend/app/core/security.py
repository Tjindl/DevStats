import base64
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any

from app.core.config import settings
from cryptography.fernet import Fernet, InvalidToken
from fastapi import HTTPException, status
from jose import JWTError, jwt


def _fernet_key() -> bytes:
    """
    Derive a Fernet key from the JWT secret so we do not persist
    multiple secrets.
    """
    if not settings.jwt_secret:
        raise RuntimeError(
            "JWT_SECRET is required for encryption and signing.")
    digest = hashlib.sha256(settings.jwt_secret.encode()).digest()
    return base64.urlsafe_b64encode(digest)


def encrypt_token(token: str) -> str:
    """Encrypt sensitive tokens before storing."""
    fernet = Fernet(_fernet_key())
    return fernet.encrypt(token.encode()).decode()


def decrypt_token(token_encrypted: str) -> str:
    """Decrypt stored tokens."""
    fernet = Fernet(_fernet_key())
    try:
        return fernet.decrypt(token_encrypted.encode()).decode()
    except InvalidToken as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid stored credentials.",
        ) from exc


def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    """Create a short-lived JWT for API access."""
    if not settings.jwt_secret:
        raise RuntimeError("JWT_SECRET is not configured.")
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(hours=6))
    to_encode.update({"exp": expire})
    return str(jwt.encode(to_encode, settings.jwt_secret, algorithm="HS256"))


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and validate JWT."""
    if not settings.jwt_secret:
        raise RuntimeError("JWT_SECRET is not configured.")
    try:
        return dict(
            jwt.decode(
                token,
                settings.jwt_secret,
                algorithms=["HS256"]
            )
        )
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        ) from exc

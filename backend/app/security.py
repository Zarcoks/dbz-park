"""Passwords and tokens.

The token is a signed JWT: nothing is stored, the signature is the proof. That is what
makes the back stateless — and why a token cannot be revoked, hence no logout route.
"""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.config import get_settings

settings = get_settings()

# bcrypt only reads the first 72 bytes; refuse beyond rather than truncate silently.
MAX_PASSWORD_BYTES = 72


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), password_hash.encode())
    except ValueError:
        # Unreadable hash in the database: refuse, do not raise.
        return False


def create_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    # `sub` must be a string, the JWT spec says so.
    payload = {"sub": str(user_id), "iat": now, "exp": now + timedelta(minutes=settings.jwt_ttl_minutes)}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def read_token(token: str) -> int | None:
    """The bearer's id, or `None` if the token is missing, forged or expired.

    The three cases are not told apart: the caller has no business knowing which.
    """
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
        return None

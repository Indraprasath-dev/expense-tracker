import logging
import secrets
from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

from app.core.config import settings
from app.exceptions.errors import InvalidToken, TokenExpired

logger = logging.getLogger(__name__)

ALGORITHM = "HS256"

_password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return _password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return _password_hash.verify(password, hashed_password)


# Checked when a login email is unknown, so that failure takes as long as a wrong password.
DUMMY_PASSWORD_HASH = hash_password(secrets.token_urlsafe(32))


def create_access_token(user_id: int) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY.get_secret_value(), algorithm=ALGORITHM)


def decode_access_token(token: str) -> int:
    """The user id inside a valid token. Raises TokenExpired or InvalidToken otherwise."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY.get_secret_value(),
            algorithms=[ALGORITHM],
            options={"require": ["exp", "iat", "sub"]},
        )
    except jwt.ExpiredSignatureError:
        logger.warning("Token rejected: expired")
        raise TokenExpired() from None
    except jwt.InvalidTokenError as exc:
        logger.warning("Token rejected: %s", type(exc).__name__)
        raise InvalidToken() from None

    try:
        return int(payload["sub"])
    except ValueError:
        logger.warning("Token rejected: subject is not a user id")
        raise InvalidToken() from None

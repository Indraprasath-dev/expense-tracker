import logging
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.models import User
from app.db.session import get_db
from app.exceptions.errors import InvalidToken, NotAuthenticated

logger = logging.getLogger(__name__)

DbSession = Annotated[Session, Depends(get_db)]

# auto_error=False: a missing token raises our own NotAuthenticated, in the app's error format.
_bearer_scheme = HTTPBearer(
    auto_error=False, description="Paste the access_token from POST /api/v1/auth/login"
)


def get_current_user_id(
    db: DbSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)],
) -> int:
    """The logged-in user's id, taken from the Bearer token in the Authorization header."""
    if credentials is None:
        raise NotAuthenticated()
    user_id = decode_access_token(credentials.credentials)
    if db.get(User, user_id) is None:
        logger.warning("Token rejected: user_id=%s does not exist", user_id)
        raise InvalidToken()
    return user_id


# The logged-in user's id, read from the token (no longer a ?user_id= query parameter).
UserId = Annotated[int, Depends(get_current_user_id)]

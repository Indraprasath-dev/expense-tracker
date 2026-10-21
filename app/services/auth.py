import logging

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import DUMMY_PASSWORD_HASH, create_access_token, verify_password
from app.exceptions.errors import InvalidCredentials
from app.schemas.auth import LoginRequest, TokenResponse
from app.services import user as user_service

logger = logging.getLogger(__name__)


def login(db: Session, data: LoginRequest) -> TokenResponse:
    user = user_service.get_by_email(db, data.email)
    # Check a password even when the email is unknown, so the response time doesn't reveal it.
    hashed_password = user.hashed_password if user else DUMMY_PASSWORD_HASH
    if not verify_password(data.password, hashed_password) or user is None:
        logger.warning("Login failed: incorrect email or password")
        raise InvalidCredentials()

    logger.info("User logged in: user_id=%s", user.id)
    return TokenResponse(
        access_token=create_access_token(user.id),
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

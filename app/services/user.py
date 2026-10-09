import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import EmailAlreadyExists
from app.core.security import hash_password
from app.db.models import User
from app.schemas.user import UserCreate

logger = logging.getLogger(__name__)


def get_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email.strip().lower()))


def create_user(db: Session, data: UserCreate) -> User:
    if get_by_email(db, data.email) is not None:
        logger.warning("User not created: email already registered")
        raise EmailAlreadyExists()

    user = User(
        email=data.email.strip().lower(),
        name=data.name.strip(),
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    logger.info("User created successfully: user_id=%s", user.id)
    return user

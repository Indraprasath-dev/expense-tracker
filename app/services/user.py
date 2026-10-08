from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.models import User
from app.schemas.user import UserCreate


class EmailAlreadyExists(Exception):
    pass


def get_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email.strip().lower()))


def create_user(db: Session, data: UserCreate) -> User:
    if get_by_email(db, data.email) is not None:
        raise EmailAlreadyExists(data.email)

    user = User(
        email=data.email.strip().lower(),
        name=data.name.strip(),
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        # Two requests with the same email can pass the check above at the same time.
        db.rollback()
        raise EmailAlreadyExists(data.email) from None
    return user

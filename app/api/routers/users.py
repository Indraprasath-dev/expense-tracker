from fastapi import APIRouter, status

from app.api.deps import DbSession
from app.schemas.user import UserCreate, UserRead
from app.services import user as user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(body: UserCreate, db: DbSession):
    return user_service.create_user(db, body)

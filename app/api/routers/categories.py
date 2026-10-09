from fastapi import APIRouter, status

from app.api.deps import DbSession, UserId
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.services import category as category_service

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(body: CategoryCreate, user_id: UserId, db: DbSession):
    return category_service.create_category(db, user_id, body)


@router.get("", response_model=list[CategoryRead])
def list_categories(user_id: UserId, db: DbSession, is_archived: bool = False):
    return category_service.list_categories(db, user_id, is_archived)


@router.get("/{category_id}", response_model=CategoryRead)
def get_category(category_id: int, user_id: UserId, db: DbSession):
    return category_service.get_category(db, user_id, category_id)


@router.patch("/{category_id}", response_model=CategoryRead)
def update_category(category_id: int, body: CategoryUpdate, user_id: UserId, db: DbSession):
    return category_service.update_category(db, user_id, category_id, body)

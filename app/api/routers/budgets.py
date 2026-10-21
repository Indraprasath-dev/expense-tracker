from fastapi import APIRouter, status

from app.api.deps import DbSession, UserId
from app.schemas.budget import BudgetCreate, BudgetRead, BudgetUpdate
from app.services import budget as budget_service

router = APIRouter(prefix="/budgets", tags=["budgets"])


@router.post("", response_model=BudgetRead, status_code=status.HTTP_201_CREATED)
def create_budget(body: BudgetCreate, user_id: UserId, db: DbSession):
    return budget_service.create_budget(db, user_id, body)


@router.get("", response_model=list[BudgetRead])
def list_budgets(user_id: UserId, db: DbSession):
    return budget_service.list_budgets(db, user_id)


@router.get("/{budget_id}", response_model=BudgetRead)
def get_budget(budget_id: int, user_id: UserId, db: DbSession):
    return budget_service.get_budget(db, user_id, budget_id)


@router.patch("/{budget_id}", response_model=BudgetRead)
def update_budget(budget_id: int, body: BudgetUpdate, user_id: UserId, db: DbSession):
    return budget_service.update_budget(db, user_id, budget_id, body)

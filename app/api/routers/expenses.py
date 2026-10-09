from fastapi import APIRouter, status

from app.api.deps import DbSession, UserId
from app.schemas.expense import ExpenseCreate, ExpenseRead, ExpenseUpdate
from app.services import expense as expense_service

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.post("", response_model=ExpenseRead, status_code=status.HTTP_201_CREATED)
def create_expense(body: ExpenseCreate, user_id: UserId, db: DbSession):
    return expense_service.create_expense(db, user_id, body)


@router.get("", response_model=list[ExpenseRead])
def list_expenses(user_id: UserId, db: DbSession):
    return expense_service.list_expenses(db, user_id)


@router.get("/{expense_id}", response_model=ExpenseRead)
def get_expense(expense_id: int, user_id: UserId, db: DbSession):
    return expense_service.get_expense(db, user_id, expense_id)


@router.patch("/{expense_id}", response_model=ExpenseRead)
def update_expense(expense_id: int, body: ExpenseUpdate, user_id: UserId, db: DbSession):
    return expense_service.update_expense(db, user_id, expense_id, body)

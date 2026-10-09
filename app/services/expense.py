import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import ExpenseNotFound, UserNotFound
from app.db.models import Expense, User
from app.schemas.expense import ExpenseCreate, ExpenseUpdate
from app.services import category as category_service

logger = logging.getLogger(__name__)


def create_expense(db: Session, user_id: int, data: ExpenseCreate) -> Expense:
    logger.info(
        "Creating expense: user_id=%s category_id=%s amount=%s expense_date=%s",
        user_id,
        data.category_id,
        data.amount,
        data.expense_date,
    )
    if db.get(User, user_id) is None:
        logger.warning("Expense not created: user_id=%s does not exist", user_id)
        raise UserNotFound()
    category_service.get_active_category(db, user_id, data.category_id)

    expense = Expense(user_id=user_id, **data.model_dump())
    db.add(expense)
    db.commit()
    db.refresh(expense)  # read back what the database stored (e.g. amount 100 -> 100.00)
    logger.info(
        "Expense created successfully: expense_id=%s user_id=%s category_id=%s amount=%s",
        expense.id,
        user_id,
        expense.category_id,
        expense.amount,
    )
    return expense


def list_expenses(db: Session, user_id: int) -> list[Expense]:
    logger.info("Listing expenses: user_id=%s", user_id)
    query = (
        select(Expense)
        .where(Expense.user_id == user_id)
        .order_by(Expense.expense_date.desc(), Expense.id.desc())
    )
    expenses = list(db.scalars(query))
    logger.debug("Expenses listed: user_id=%s count=%s", user_id, len(expenses))
    return expenses


def get_expense(db: Session, user_id: int, expense_id: int) -> Expense:
    logger.info("Fetching expense: expense_id=%s user_id=%s", expense_id, user_id)
    expense = db.scalar(select(Expense).where(Expense.id == expense_id, Expense.user_id == user_id))
    if expense is None:
        logger.warning(
            "Expense not found: expense_id=%s does not exist for user_id=%s", expense_id, user_id
        )
        raise ExpenseNotFound()
    return expense


def update_expense(db: Session, user_id: int, expense_id: int, data: ExpenseUpdate) -> Expense:
    logger.info(
        "Updating expense: expense_id=%s user_id=%s fields=%s",
        expense_id,
        user_id,
        sorted(data.model_fields_set),
    )
    expense = get_expense(db, user_id, expense_id)
    changes = data.model_dump(exclude_unset=True)

    if "category_id" in changes and changes["category_id"] != expense.category_id:
        category_service.get_active_category(db, user_id, changes["category_id"])

    for field, value in changes.items():
        setattr(expense, field, value)
    db.commit()
    db.refresh(expense)
    logger.info(
        "Expense updated successfully: expense_id=%s user_id=%s changed_fields=%s",
        expense_id,
        user_id,
        sorted(changes),
    )
    return expense

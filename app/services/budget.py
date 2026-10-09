import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import Month
from app.core.exceptions import BudgetAlreadyExists, BudgetNotFound, UserNotFound
from app.db.models import Budget, User
from app.schemas.budget import BudgetCreate, BudgetUpdate
from app.services import category as category_service

logger = logging.getLogger(__name__)


def _budget_exists(db: Session, category_id: int, month: Month, exclude_id: int | None = None) -> bool:
    query = select(Budget.id).where(Budget.category_id == category_id, Budget.month == month)
    if exclude_id is not None:
        query = query.where(Budget.id != exclude_id)
    return db.scalar(query) is not None


def create_budget(db: Session, user_id: int, data: BudgetCreate) -> Budget:
    logger.info(
        "Creating budget: user_id=%s category_id=%s month=%s amount=%s",
        user_id,
        data.category_id,
        data.month.value,
        data.amount,
    )
    if db.get(User, user_id) is None:
        logger.warning("Budget not created: user_id=%s does not exist", user_id)
        raise UserNotFound()
    category_service.get_active_category(db, user_id, data.category_id)
    if _budget_exists(db, data.category_id, data.month):
        logger.warning(
            "Budget not created: category_id=%s already has a budget for month=%s",
            data.category_id,
            data.month.value,
        )
        raise BudgetAlreadyExists()

    budget = Budget(user_id=user_id, **data.model_dump())
    db.add(budget)
    db.commit()
    db.refresh(budget)  # read back what the database stored (e.g. amount 100 -> 100.00)
    logger.info(
        "Budget created successfully: budget_id=%s user_id=%s category_id=%s month=%s amount=%s",
        budget.id,
        user_id,
        budget.category_id,
        budget.month.value,
        budget.amount,
    )
    return budget


def list_budgets(db: Session, user_id: int) -> list[Budget]:
    logger.info("Listing budgets: user_id=%s", user_id)
    budgets = db.scalars(select(Budget).where(Budget.user_id == user_id))
    calendar = list(Month)  # sort January to December, not alphabetically
    result = sorted(budgets, key=lambda b: (calendar.index(b.month), b.category_id))
    logger.debug("Budgets listed: user_id=%s count=%s", user_id, len(result))
    return result


def get_budget(db: Session, user_id: int, budget_id: int) -> Budget:
    logger.info("Fetching budget: budget_id=%s user_id=%s", budget_id, user_id)
    budget = db.scalar(select(Budget).where(Budget.id == budget_id, Budget.user_id == user_id))
    if budget is None:
        logger.warning(
            "Budget not found: budget_id=%s does not exist for user_id=%s", budget_id, user_id
        )
        raise BudgetNotFound()
    return budget


def update_budget(db: Session, user_id: int, budget_id: int, data: BudgetUpdate) -> Budget:
    logger.info(
        "Updating budget: budget_id=%s user_id=%s fields=%s",
        budget_id,
        user_id,
        sorted(data.model_fields_set),
    )
    budget = get_budget(db, user_id, budget_id)
    changes = data.model_dump(exclude_unset=True)

    if "category_id" in changes and changes["category_id"] != budget.category_id:
        category_service.get_active_category(db, user_id, changes["category_id"])
    new_category = changes.get("category_id", budget.category_id)
    new_month = changes.get("month", budget.month)
    if _budget_exists(db, new_category, new_month, exclude_id=budget.id):
        logger.warning(
            "Budget not updated: budget_id=%s, category_id=%s already has another budget for month=%s",
            budget_id,
            new_category,
            new_month.value,
        )
        raise BudgetAlreadyExists()

    for field, value in changes.items():
        setattr(budget, field, value)
    db.commit()
    db.refresh(budget)
    logger.info(
        "Budget updated successfully: budget_id=%s user_id=%s changed_fields=%s",
        budget_id,
        user_id,
        sorted(changes),
    )
    return budget

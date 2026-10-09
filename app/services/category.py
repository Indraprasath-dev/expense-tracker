import logging

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import (
    CategoryArchived,
    CategoryNameExists,
    CategoryNotFound,
    UserNotFound,
)
from app.db.models import Category, User
from app.schemas.category import CategoryCreate, CategoryUpdate

logger = logging.getLogger(__name__)


def _name_in_use(db: Session, user_id: int, name: str, exclude_id: int | None = None) -> bool:
    """True if the user already has an active category with this name (ignoring case)."""
    query = select(Category.id).where(
        Category.user_id == user_id,
        Category.is_archived.is_(False),
        func.lower(Category.name) == name.lower(),
    )
    if exclude_id is not None:
        query = query.where(Category.id != exclude_id)
    return db.scalar(query) is not None


def create_category(db: Session, user_id: int, data: CategoryCreate) -> Category:
    logger.info("Creating category: user_id=%s name=%r", user_id, data.name)
    if db.get(User, user_id) is None:
        logger.warning("Category not created: user_id=%s does not exist", user_id)
        raise UserNotFound()
    name = data.name.strip()
    if _name_in_use(db, user_id, name):
        logger.warning(
            "Category not created: user_id=%s already has an active category named %r", user_id, name
        )
        raise CategoryNameExists()

    category = Category(user_id=user_id, name=name, description=data.description)
    db.add(category)
    db.commit()
    logger.info(
        "Category created successfully: category_id=%s user_id=%s name=%r", category.id, user_id, name
    )
    return category


def list_categories(db: Session, user_id: int, is_archived: bool = False) -> list[Category]:
    logger.info("Listing categories: user_id=%s is_archived=%s", user_id, is_archived)
    query = (
        select(Category)
        .where(Category.user_id == user_id, Category.is_archived.is_(is_archived))
        .order_by(Category.name)
    )
    categories = list(db.scalars(query))
    logger.debug(
        "Categories listed: user_id=%s is_archived=%s count=%s", user_id, is_archived, len(categories)
    )
    return categories


def get_category(db: Session, user_id: int, category_id: int) -> Category:
    category = db.scalar(
        select(Category).where(Category.id == category_id, Category.user_id == user_id)
    )
    if category is None:
        logger.warning(
            "Category not found: category_id=%s does not exist for user_id=%s", category_id, user_id
        )
        raise CategoryNotFound()
    return category


def get_active_category(db: Session, user_id: int, category_id: int) -> Category:
    """The user's category, which must exist and not be archived (for new expenses and budgets)."""
    category = get_category(db, user_id, category_id)
    if category.is_archived:
        logger.warning(
            "Category rejected: category_id=%s of user_id=%s is archived", category_id, user_id
        )
        raise CategoryArchived()
    return category


def update_category(
    db: Session, user_id: int, category_id: int, data: CategoryUpdate
) -> Category:
    logger.info(
        "Updating category: category_id=%s user_id=%s fields=%s",
        category_id,
        user_id,
        sorted(data.model_fields_set),
    )
    category = get_category(db, user_id, category_id)
    changes = data.model_dump(exclude_unset=True)
    if "name" in changes:
        changes["name"] = changes["name"].strip()

    will_be_archived = changes.get("is_archived", category.is_archived)
    new_name = changes.get("name", category.name)
    if not will_be_archived and _name_in_use(db, user_id, new_name, exclude_id=category.id):
        logger.warning(
            "Category not updated: category_id=%s user_id=%s, another active category is already named %r",
            category_id,
            user_id,
            new_name,
        )
        raise CategoryNameExists()

    for field, value in changes.items():
        setattr(category, field, value)
    db.commit()
    logger.info(
        "Category updated successfully: category_id=%s user_id=%s changed_fields=%s is_archived=%s",
        category_id,
        user_id,
        sorted(changes),
        category.is_archived,
    )
    return category

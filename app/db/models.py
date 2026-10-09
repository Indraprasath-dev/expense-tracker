from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    ForeignKeyConstraint,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    false,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import Month, PaymentMethod
from app.db.base import Base


def _now() -> datetime:
    return datetime.now(UTC)


class User(Base):
    """An app user who owns categories, expenses and budgets."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    categories: Mapped[list["Category"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    expenses: Mapped[list["Expense"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    budgets: Mapped[list["Budget"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Category(Base):
    """A label used to group expenses, such as Food or Travel. Archived instead of deleted."""

    __tablename__ = "categories"
    __table_args__ = (UniqueConstraint("id", "user_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text)
    is_archived: Mapped[bool] = mapped_column(Boolean, server_default=false())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    user: Mapped["User"] = relationship(back_populates="categories")
    expenses: Mapped[list["Expense"]] = relationship(back_populates="category")
    budgets: Mapped[list["Budget"]] = relationship(
        back_populates="category", cascade="all, delete-orphan"
    )


class Expense(Base):
    """A single spending record with an amount, date and category."""

    __tablename__ = "expenses"
    __table_args__ = (
        ForeignKeyConstraint(
            ["category_id", "user_id"],
            ["categories.id", "categories.user_id"],
        ),
        CheckConstraint("amount > 0", name="ck_expenses_amount_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    category_id: Mapped[int] = mapped_column(index=True)
    description: Mapped[str | None] = mapped_column(Text)
    expense_date: Mapped[date] = mapped_column(Date, index=True)
    payment_method: Mapped[PaymentMethod | None] = mapped_column(
        Enum(
            PaymentMethod,
            native_enum=False,
            length=20,
            values_callable=lambda e: [m.value for m in e],
        )
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=_now
    )

    user: Mapped["User"] = relationship(back_populates="expenses")
    category: Mapped["Category"] = relationship(back_populates="expenses", overlaps="user")


class Budget(Base):
    """A spending limit for one category in one month of the year (repeats every year)."""

    __tablename__ = "budgets"
    __table_args__ = (
        ForeignKeyConstraint(
            ["category_id", "user_id"],
            ["categories.id", "categories.user_id"],
            ondelete="CASCADE",
        ),
        UniqueConstraint("category_id", "month", name="uq_budgets_category_month"),
        CheckConstraint("amount > 0", name="ck_budgets_amount_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    category_id: Mapped[int]
    month: Mapped[Month] = mapped_column(
        Enum(Month, native_enum=False, length=10, values_callable=lambda e: [m.value for m in e])
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    user: Mapped["User"] = relationship(back_populates="budgets")
    category: Mapped["Category"] = relationship(back_populates="budgets", overlaps="user")

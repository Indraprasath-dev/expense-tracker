from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.core.enums import PaymentMethod

Amount = Annotated[Decimal, Field(gt=0, max_digits=12, decimal_places=2)]


class ExpenseCreate(BaseModel):
    amount: Amount
    category_id: int = Field(gt=0)
    expense_date: date
    description: str | None = Field(default=None, max_length=500)
    payment_method: PaymentMethod | None = None


class ExpenseUpdate(BaseModel):
    """Send only the fields you want to change."""

    amount: Amount | None = None
    category_id: int | None = Field(default=None, gt=0)
    expense_date: date | None = None
    description: str | None = Field(default=None, max_length=500)
    payment_method: PaymentMethod | None = None

    @model_validator(mode="after")
    def reject_null_for_required_fields(self) -> Self:
        for field in ("amount", "category_id", "expense_date"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        return self


class ExpenseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    amount: Decimal
    category_id: int
    expense_date: date
    description: str | None
    payment_method: PaymentMethod | None
    created_at: datetime
    updated_at: datetime

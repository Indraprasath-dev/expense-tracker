from datetime import datetime
from decimal import Decimal
from typing import Annotated, Self

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, model_validator

from app.core.enums import Month

Amount = Annotated[Decimal, Field(gt=0, max_digits=12, decimal_places=2)]
# "October", "OCTOBER" and " october " are all turned into "october" before they are checked and saved.
MonthName = Annotated[Month, BeforeValidator(lambda v: v.strip().lower() if isinstance(v, str) else v)]


class BudgetCreate(BaseModel):
    category_id: int = Field(gt=0)
    month: MonthName
    amount: Amount


class BudgetUpdate(BaseModel):
    """Send only the fields you want to change."""

    category_id: int | None = Field(default=None, gt=0)
    month: MonthName | None = None
    amount: Amount | None = None

    @model_validator(mode="after")
    def reject_null_for_required_fields(self) -> Self:
        for field in ("category_id", "month", "amount"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        return self


class BudgetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: int
    month: Month
    amount: Decimal
    created_at: datetime

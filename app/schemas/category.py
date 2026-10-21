from datetime import datetime
from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

CategoryName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]


class CategoryCreate(BaseModel):
    name: CategoryName
    description: str | None = Field(default=None, max_length=500)


class CategoryUpdate(BaseModel):
    """Send only the fields you want to change."""

    name: CategoryName | None = None
    description: str | None = Field(default=None, max_length=500)
    is_archived: bool | None = Field(default=None, description="false restores an archived category")

    @model_validator(mode="after")
    def reject_null_for_required_fields(self) -> Self:
        for field in ("name", "is_archived"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        return self


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    is_archived: bool
    created_at: datetime

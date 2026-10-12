from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ExpenseBase(BaseModel):
    amount: Decimal = Field(..., gt=0, max_digits=12, decimal_places=2)
    currency: str = Field(default="EUR", min_length=3, max_length=3)
    description: str | None = Field(default=None, max_length=255)
    occurred_on: date
    source: str = Field(default="manual", max_length=64)
    external_id: str | None = Field(default=None, max_length=128)


class ExpenseCreate(ExpenseBase):
    category_id: int


class ExpenseUpdate(BaseModel):
    amount: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    description: str | None = Field(default=None, max_length=255)
    occurred_on: date | None = None
    category_id: int | None = None


class ExpenseRead(ExpenseBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: int
    created_at: datetime

from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class CategoryTotal(BaseModel):
    category_id: int
    category_name: str
    total: Decimal
    count: int


class MonthlyTotal(BaseModel):
    year: int
    month: int
    total: Decimal
    count: int


class DashboardSummary(BaseModel):
    date_from: date | None
    date_to: date | None
    grand_total: Decimal
    expense_count: int
    by_category: list[CategoryTotal]
    by_month: list[MonthlyTotal]

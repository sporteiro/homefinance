from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class CategoryTotal(BaseModel):
    category_id: int
    category_name: str
    total: Decimal
    count: int


class CategoryStatistics(BaseModel):
    category_name: str
    total: Decimal
    count: int
    mean: Decimal
    median: Decimal
    mode: Decimal


class MonthCategoryRow(BaseModel):
    year: int
    month: int
    label: str
    total: Decimal
    per_category: dict[str, Decimal]


class YearCategoryRow(BaseModel):
    year: int
    total: Decimal
    per_category: dict[str, Decimal]


class DashboardSummary(BaseModel):
    date_from: date | None
    date_to: date | None
    grand_total: Decimal
    expense_count: int
    category_names: list[str]
    by_category: list[CategoryTotal]
    category_statistics: list[CategoryStatistics]
    months_last_12: list[MonthCategoryRow]
    years_last_10: list[YearCategoryRow]
    years_table: list[YearCategoryRow]

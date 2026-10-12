from datetime import date
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Category, Expense
from app.schemas import (
    CategoryStatistics,
    CategoryTotal,
    DashboardSummary,
    MonthCategoryRow,
    YearCategoryRow,
)
from app.services.statistics_calculator import StatisticsCalculator

MONTHS_LAST_12 = 12
YEARS_LAST_10 = 10


class DashboardService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def build_summary(
        self,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> DashboardSummary:
        category_names = [row.name for row in self._ordered_categories()]

        return DashboardSummary(
            date_from=date_from,
            date_to=date_to,
            grand_total=self._grand_total(date_from, date_to),
            expense_count=self._expense_count(date_from, date_to),
            category_names=category_names,
            by_category=self._totals_by_category(date_from, date_to),
            category_statistics=self._category_statistics(date_from, date_to),
            months_last_12=self._months_last_12(),
            years_last_10=self._years_last_10(),
            years_table=self._years_table(date_from, date_to),
        )

    def _base_query(self, date_from: date | None, date_to: date | None):
        query = self.session.query(Expense)
        if date_from is not None:
            query = query.filter(Expense.occurred_on >= date_from)
        if date_to is not None:
            query = query.filter(Expense.occurred_on <= date_to)
        return query

    def _ordered_categories(self) -> list[Category]:
        return self.session.query(Category).order_by(Category.name).all()

    def _grand_total(
        self, date_from: date | None, date_to: date | None
    ) -> Decimal:
        total = (
            self._base_query(date_from, date_to)
            .with_entities(func.coalesce(func.sum(Expense.amount), 0))
            .scalar()
        )
        return Decimal(total or 0)

    def _expense_count(
        self, date_from: date | None, date_to: date | None
    ) -> int:
        return (
            self._base_query(date_from, date_to)
            .with_entities(func.count(Expense.id))
            .scalar()
            or 0
        )

    def _totals_by_category(
        self, date_from: date | None, date_to: date | None
    ) -> list[CategoryTotal]:
        rows = (
            self._base_query(date_from, date_to)
            .join(Category, Category.id == Expense.category_id)
            .with_entities(
                Category.id,
                Category.name,
                func.sum(Expense.amount),
                func.count(Expense.id),
            )
            .group_by(Category.id, Category.name)
            .order_by(func.sum(Expense.amount).desc())
            .all()
        )

        return [
            CategoryTotal(
                category_id=row[0],
                category_name=row[1],
                total=Decimal(row[2] or 0),
                count=row[3],
            )
            for row in rows
        ]

    def _category_statistics(
        self, date_from: date | None, date_to: date | None
    ) -> list[CategoryStatistics]:
        rows = (
            self._base_query(date_from, date_to)
            .join(Category, Category.id == Expense.category_id)
            .with_entities(Category.name, Expense.amount)
            .order_by(Category.name)
            .all()
        )

        grouped: dict[str, list[Decimal]] = {}
        for name, amount in rows:
            grouped.setdefault(name, []).append(Decimal(amount))

        results: list[CategoryStatistics] = []
        for name in sorted(grouped.keys()):
            values = grouped[name]
            total = sum(values, Decimal("0"))
            results.append(
                CategoryStatistics(
                    category_name=name,
                    total=total,
                    count=len(values),
                    mean=StatisticsCalculator.mean(values),
                    median=StatisticsCalculator.median(values),
                    mode=StatisticsCalculator.mode(values),
                )
            )
        return results

    def _months_last_12(self) -> list[MonthCategoryRow]:
        rows = (
            self.session.query(
                func.extract("year", Expense.occurred_on).label("year"),
                func.extract("month", Expense.occurred_on).label("month"),
                Category.name.label("category_name"),
                func.sum(Expense.amount).label("total"),
            )
            .join(Category, Category.id == Expense.category_id)
            .group_by("year", "month", Category.name)
            .order_by("year", "month")
            .all()
        )

        aggregated: dict[tuple[int, int], dict[str, Decimal]] = {}
        for row in rows:
            key = (int(row.year), int(row.month))
            aggregated.setdefault(key, {})
            aggregated[key][row.category_name] = Decimal(row.total or 0)

        ordered_keys = sorted(aggregated.keys())[-MONTHS_LAST_12:]

        result: list[MonthCategoryRow] = []
        for year, month in ordered_keys:
            per_category = aggregated[(year, month)]
            result.append(
                MonthCategoryRow(
                    year=year,
                    month=month,
                    label=f"{year}-{month:02d}",
                    total=sum(per_category.values(), Decimal("0")),
                    per_category=per_category,
                )
            )
        return result

    def _years_last_10(self) -> list[YearCategoryRow]:
        rows = (
            self.session.query(
                func.extract("year", Expense.occurred_on).label("year"),
                Category.name.label("category_name"),
                func.sum(Expense.amount).label("total"),
            )
            .join(Category, Category.id == Expense.category_id)
            .group_by("year", Category.name)
            .order_by("year")
            .all()
        )

        aggregated: dict[int, dict[str, Decimal]] = {}
        for row in rows:
            year = int(row.year)
            aggregated.setdefault(year, {})
            aggregated[year][row.category_name] = Decimal(row.total or 0)

        ordered_years = sorted(aggregated.keys())[-YEARS_LAST_10:]

        result: list[YearCategoryRow] = []
        for year in ordered_years:
            per_category = aggregated[year]
            result.append(
                YearCategoryRow(
                    year=year,
                    total=sum(per_category.values(), Decimal("0")),
                    per_category=per_category,
                )
            )
        return result

    def _years_table(
        self, date_from: date | None, date_to: date | None
    ) -> list[YearCategoryRow]:
        rows = (
            self._base_query(date_from, date_to)
            .with_entities(
                func.extract("year", Expense.occurred_on).label("year"),
                Category.name.label("category_name"),
                func.sum(Expense.amount).label("total"),
            )
            .join(Category, Category.id == Expense.category_id)
            .group_by("year", Category.name)
            .order_by("year")
            .all()
        )

        aggregated: dict[int, dict[str, Decimal]] = {}
        for row in rows:
            year = int(row.year)
            aggregated.setdefault(year, {})
            aggregated[year][row.category_name] = Decimal(row.total or 0)

        result: list[YearCategoryRow] = []
        for year in sorted(aggregated.keys()):
            per_category = aggregated[year]
            result.append(
                YearCategoryRow(
                    year=year,
                    total=sum(per_category.values(), Decimal("0")),
                    per_category=per_category,
                )
            )
        return result

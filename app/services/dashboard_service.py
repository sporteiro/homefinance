from datetime import date
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Category, Expense
from app.schemas import CategoryTotal, DashboardSummary, MonthlyTotal


class DashboardService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def build_summary(
        self,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> DashboardSummary:
        return DashboardSummary(
            date_from=date_from,
            date_to=date_to,
            grand_total=self._grand_total(date_from, date_to),
            expense_count=self._expense_count(date_from, date_to),
            by_category=self._totals_by_category(date_from, date_to),
            by_month=self._totals_by_month(date_from, date_to),
        )

    def _base_query(self, date_from: date | None, date_to: date | None):
        query = self.session.query(Expense)
        if date_from is not None:
            query = query.filter(Expense.occurred_on >= date_from)
        if date_to is not None:
            query = query.filter(Expense.occurred_on <= date_to)
        return query

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

    def _totals_by_month(
        self, date_from: date | None, date_to: date | None
    ) -> list[MonthlyTotal]:
        year = func.extract("year", Expense.occurred_on)
        month = func.extract("month", Expense.occurred_on)

        rows = (
            self._base_query(date_from, date_to)
            .with_entities(
                year.label("year"),
                month.label("month"),
                func.sum(Expense.amount),
                func.count(Expense.id),
            )
            .group_by(year, month)
            .order_by(year, month)
            .all()
        )

        return [
            MonthlyTotal(
                year=int(row[0]),
                month=int(row[1]),
                total=Decimal(row[2] or 0),
                count=row[3],
            )
            for row in rows
        ]

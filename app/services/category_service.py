from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Category, Expense
from app.schemas import CategoryCreate, CategoryUpdate


class CategoryStats:
    def __init__(
        self,
        category: Category,
        expense_count: int,
        total_spent: Decimal,
        months_in_range: int,
        years_in_range: int,
    ) -> None:
        self.category = category
        self.expense_count = expense_count
        self.total_spent = total_spent
        self.months_in_range = months_in_range
        self.years_in_range = years_in_range

    @property
    def average_per_month(self) -> Decimal:
        if self.months_in_range == 0:
            return Decimal("0")
        return (self.total_spent / Decimal(self.months_in_range)).quantize(
            Decimal("0.01")
        )

    @property
    def average_per_year(self) -> Decimal:
        if self.years_in_range == 0:
            return Decimal("0")
        return (self.total_spent / Decimal(self.years_in_range)).quantize(
            Decimal("0.01")
        )


def _months_between(first_year: int, first_month: int, last_year: int, last_month: int) -> int:
    return (last_year - first_year) * 12 + (last_month - first_month) + 1


class CategoryService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_all(self) -> list[Category]:
        return self.session.query(Category).order_by(Category.name).all()

    def get_by_id(self, category_id: int) -> Category | None:
        return self.session.get(Category, category_id)

    def get_by_name(self, name: str) -> Category | None:
        return (
            self.session.query(Category)
            .filter(Category.name == name)
            .one_or_none()
        )

    def create(self, payload: CategoryCreate) -> Category:
        category = Category(
            name=payload.name,
            description=payload.description,
        )
        self.session.add(category)
        self.session.commit()
        self.session.refresh(category)
        return category

    def update(self, category_id: int, payload: CategoryUpdate) -> Category | None:
        category = self.get_by_id(category_id)
        if category is None:
            return None

        data = payload.model_dump(exclude_unset=True)
        for field, value in data.items():
            setattr(category, field, value)

        self.session.commit()
        self.session.refresh(category)
        return category

    def delete(self, category_id: int) -> bool:
        category = self.get_by_id(category_id)
        if category is None:
            return False

        self.session.delete(category)
        self.session.commit()
        return True

    def get_or_create(self, name: str) -> Category:
        category = self.get_by_name(name)
        if category is not None:
            return category

        category = Category(name=name)
        self.session.add(category)
        self.session.commit()
        self.session.refresh(category)
        return category

    def list_with_stats(self) -> list[CategoryStats]:
        rows = (
            self.session.query(
                Category,
                func.count(Expense.id),
                func.coalesce(func.sum(Expense.amount), 0),
                func.min(Expense.occurred_on),
                func.max(Expense.occurred_on),
            )
            .outerjoin(Expense, Expense.category_id == Category.id)
            .group_by(Category.id)
            .order_by(Category.name)
            .all()
        )

        stats: list[CategoryStats] = []
        for row in rows:
            category = row[0]
            expense_count = int(row[1] or 0)
            total_spent = Decimal(row[2] or 0)
            first_date = row[3]
            last_date = row[4]

            if first_date is None or last_date is None:
                months_in_range = 0
                years_in_range = 0
            else:
                months_in_range = _months_between(
                    first_date.year,
                    first_date.month,
                    last_date.year,
                    last_date.month,
                )
                years_in_range = last_date.year - first_date.year + 1

            stats.append(
                CategoryStats(
                    category=category,
                    expense_count=expense_count,
                    total_spent=total_spent,
                    months_in_range=months_in_range,
                    years_in_range=years_in_range,
                )
            )
        return stats

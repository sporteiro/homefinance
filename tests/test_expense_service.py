from datetime import date
from decimal import Decimal

from app.schemas import CategoryCreate, ExpenseCreate
from app.services import CategoryService, ExpenseService


def test_create_expense_with_category(session):
    categories = CategoryService(session)
    expenses = ExpenseService(session)

    category = categories.create(CategoryCreate(name="Food"))
    expense = expenses.create(
        ExpenseCreate(
            amount=Decimal("25.00"),
            currency="EUR",
            description="Groceries",
            occurred_on=date(2024, 2, 1),
            source="manual",
            external_id=None,
            category_id=category.id,
        )
    )

    assert expense.id is not None
    assert expense.category_id == category.id


def test_list_expenses_filters_by_date(session):
    categories = CategoryService(session)
    expenses = ExpenseService(session)

    category = categories.create(CategoryCreate(name="Internet"))
    expenses.create(
        ExpenseCreate(
            amount=Decimal("30.00"),
            currency="EUR",
            description="January",
            occurred_on=date(2024, 1, 5),
            source="manual",
            external_id=None,
            category_id=category.id,
        )
    )
    expenses.create(
        ExpenseCreate(
            amount=Decimal("30.00"),
            currency="EUR",
            description="February",
            occurred_on=date(2024, 2, 5),
            source="manual",
            external_id=None,
            category_id=category.id,
        )
    )

    results = expenses.list_all(date_from=date(2024, 2, 1))

    assert len(results) == 1
    assert results[0].description == "February"

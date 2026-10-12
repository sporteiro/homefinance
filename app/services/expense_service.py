from datetime import date

from sqlalchemy.orm import Session

from app.models import Expense
from app.schemas import ExpenseCreate, ExpenseUpdate


class ExpenseService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_all(
        self,
        category_id: int | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> list[Expense]:
        query = self.session.query(Expense)

        if category_id is not None:
            query = query.filter(Expense.category_id == category_id)
        if date_from is not None:
            query = query.filter(Expense.occurred_on >= date_from)
        if date_to is not None:
            query = query.filter(Expense.occurred_on <= date_to)

        return query.order_by(Expense.occurred_on.desc()).all()

    def get_by_id(self, expense_id: int) -> Expense | None:
        return self.session.get(Expense, expense_id)

    def exists_by_external_id(self, external_id: str) -> bool:
        return (
            self.session.query(Expense)
            .filter(Expense.external_id == external_id)
            .first()
            is not None
        )

    def create(self, payload: ExpenseCreate) -> Expense:
        expense = Expense(**payload.model_dump())
        self.session.add(expense)
        self.session.commit()
        self.session.refresh(expense)
        return expense

    def update(self, expense_id: int, payload: ExpenseUpdate) -> Expense | None:
        expense = self.get_by_id(expense_id)
        if expense is None:
            return None

        data = payload.model_dump(exclude_unset=True)
        for field, value in data.items():
            setattr(expense, field, value)

        self.session.commit()
        self.session.refresh(expense)
        return expense

    def delete(self, expense_id: int) -> bool:
        expense = self.get_by_id(expense_id)
        if expense is None:
            return False

        self.session.delete(expense)
        self.session.commit()
        return True

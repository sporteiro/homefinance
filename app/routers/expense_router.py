from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.routers.dependencies import get_db
from app.schemas import ExpenseCreate, ExpenseRead, ExpenseUpdate
from app.services import CategoryService, ExpenseService


class ExpenseRouter:
    def __init__(self) -> None:
        self.router = APIRouter(prefix="/api/expenses", tags=["expenses"])
        self._register_routes()

    def _register_routes(self) -> None:
        self.router.add_api_route(
            "/",
            self.list_expenses,
            methods=["GET"],
            response_model=list[ExpenseRead],
        )
        self.router.add_api_route(
            "/{expense_id}",
            self.get_expense,
            methods=["GET"],
            response_model=ExpenseRead,
        )
        self.router.add_api_route(
            "/",
            self.create_expense,
            methods=["POST"],
            response_model=ExpenseRead,
            status_code=status.HTTP_201_CREATED,
        )
        self.router.add_api_route(
            "/{expense_id}",
            self.update_expense,
            methods=["PUT"],
            response_model=ExpenseRead,
        )
        self.router.add_api_route(
            "/{expense_id}",
            self.delete_expense,
            methods=["DELETE"],
            status_code=status.HTTP_204_NO_CONTENT,
        )

    def list_expenses(
        self,
        category_id: int | None = Query(default=None),
        date_from: date | None = Query(default=None),
        date_to: date | None = Query(default=None),
        db: Session = Depends(get_db),
    ) -> list[ExpenseRead]:
        service = ExpenseService(db)
        return service.list_all(
            category_id=category_id,
            date_from=date_from,
            date_to=date_to,
        )

    def get_expense(
        self, expense_id: int, db: Session = Depends(get_db)
    ) -> ExpenseRead:
        service = ExpenseService(db)
        expense = service.get_by_id(expense_id)
        if expense is None:
            raise HTTPException(status_code=404, detail="Expense not found")
        return expense

    def create_expense(
        self, payload: ExpenseCreate, db: Session = Depends(get_db)
    ) -> ExpenseRead:
        category_service = CategoryService(db)
        if category_service.get_by_id(payload.category_id) is None:
            raise HTTPException(status_code=404, detail="Category not found")

        expense_service = ExpenseService(db)
        if payload.external_id and expense_service.exists_by_external_id(
            payload.external_id
        ):
            raise HTTPException(status_code=409, detail="Expense already imported")

        return expense_service.create(payload)

    def update_expense(
        self,
        expense_id: int,
        payload: ExpenseUpdate,
        db: Session = Depends(get_db),
    ) -> ExpenseRead:
        service = ExpenseService(db)
        expense = service.update(expense_id, payload)
        if expense is None:
            raise HTTPException(status_code=404, detail="Expense not found")
        return expense

    def delete_expense(
        self, expense_id: int, db: Session = Depends(get_db)
    ) -> None:
        service = ExpenseService(db)
        deleted = service.delete(expense_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Expense not found")


expense_router = ExpenseRouter().router

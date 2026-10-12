from datetime import date

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.routers.dependencies import get_db
from app.services import CategoryService, ExpenseService


class PagesRouter:
    def __init__(self) -> None:
        self.templates = Jinja2Templates(directory="app/templates")
        self.router = APIRouter(tags=["pages"])
        self._register_routes()

    def _register_routes(self) -> None:
        self.router.add_api_route(
            "/expenses",
            self.render_expenses,
            methods=["GET"],
            response_class=HTMLResponse,
        )
        self.router.add_api_route(
            "/categories",
            self.render_categories,
            methods=["GET"],
            response_class=HTMLResponse,
        )
        self.router.add_api_route(
            "/import",
            self.render_import,
            methods=["GET"],
            response_class=HTMLResponse,
        )

    def render_expenses(
        self,
        request: Request,
        category_id: int | None = Query(default=None),
        date_from: date | None = Query(default=None),
        date_to: date | None = Query(default=None),
        db: Session = Depends(get_db),
    ) -> HTMLResponse:
        expense_service = ExpenseService(db)
        category_service = CategoryService(db)

        expenses = expense_service.list_all(
            category_id=category_id,
            date_from=date_from,
            date_to=date_to,
        )
        categories = category_service.list_all()

        return self.templates.TemplateResponse(
            request=request,
            name="expenses.html",
            context={
                "expenses": expenses,
                "categories": categories,
                "selected_category_id": category_id,
                "date_from": date_from,
                "date_to": date_to,
            },
        )

    def render_categories(
        self,
        request: Request,
        db: Session = Depends(get_db),
    ) -> HTMLResponse:
        service = CategoryService(db)
        categories = service.list_all()

        return self.templates.TemplateResponse(
            request=request,
            name="categories.html",
            context={"categories": categories},
        )

    def render_import(self, request: Request) -> HTMLResponse:
        return self.templates.TemplateResponse(
            request=request,
            name="import.html",
            context={},
        )


pages_router = PagesRouter().router

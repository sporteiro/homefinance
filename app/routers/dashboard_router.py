from datetime import date

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.routers.dependencies import get_db
from app.schemas import DashboardSummary
from app.services import DashboardService


class DashboardRouter:
    def __init__(self) -> None:
        self.templates = Jinja2Templates(directory="app/templates")
        self.router = APIRouter(tags=["dashboard"])
        self._register_routes()

    def _register_routes(self) -> None:
        self.router.add_api_route(
            "/",
            self.render_dashboard,
            methods=["GET"],
            response_class=HTMLResponse,
        )
        self.router.add_api_route(
            "/api/dashboard/summary",
            self.summary_json,
            methods=["GET"],
            response_model=DashboardSummary,
        )

    def render_dashboard(
        self,
        request: Request,
        date_from: date | None = Query(default=None),
        date_to: date | None = Query(default=None),
        db: Session = Depends(get_db),
    ) -> HTMLResponse:
        service = DashboardService(db)
        summary = service.build_summary(date_from=date_from, date_to=date_to)

        return self.templates.TemplateResponse(
            request=request,
            name="dashboard.html",
            context={
                "summary": summary,
                "date_from": date_from,
                "date_to": date_to,
            },
        )

    def summary_json(
        self,
        date_from: date | None = Query(default=None),
        date_to: date | None = Query(default=None),
        db: Session = Depends(get_db),
    ) -> DashboardSummary:
        service = DashboardService(db)
        return service.build_summary(date_from=date_from, date_to=date_to)


dashboard_router = DashboardRouter().router

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.routers.dependencies import get_db
from app.schemas import ResetRequest, ResetResult
from app.services import CategoryService, ResetService


class AdminRouter:
    def __init__(self) -> None:
        self.templates = Jinja2Templates(directory="app/templates")
        self.router = APIRouter(tags=["admin"])
        self._register_routes()

    def _register_routes(self) -> None:
        self.router.add_api_route(
            "/admin/reset",
            self.render_reset_page,
            methods=["GET"],
            response_class=HTMLResponse,
        )
        self.router.add_api_route(
            "/api/admin/reset",
            self.reset_data,
            methods=["POST"],
            response_model=ResetResult,
        )
        self.router.add_api_route(
            "/api/admin/reset-phrase",
            self.get_confirmation_phrase,
            methods=["GET"],
        )

    def render_reset_page(
        self,
        request: Request,
        db: Session = Depends(get_db),
    ) -> HTMLResponse:
        service = CategoryService(db)
        categories = service.list_all()

        return self.templates.TemplateResponse(
            request=request,
            name="reset.html",
            context={
                "categories": categories,
                "confirmation_phrase": ResetService.CONFIRMATION_PHRASE,
            },
        )

    def get_confirmation_phrase(self) -> dict[str, str]:
        return {"phrase": ResetService.CONFIRMATION_PHRASE}

    def reset_data(
        self,
        payload: ResetRequest,
        db: Session = Depends(get_db),
    ) -> ResetResult:
        service = ResetService(db)

        if not service.is_confirmation_valid(payload):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid confirmation phrase.",
            )

        return service.reset(payload)


admin_router = AdminRouter().router

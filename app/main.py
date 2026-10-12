from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import database
from app.models import Base
from app.routers import (
    category_router,
    dashboard_router,
    expense_router,
    health_router,
    import_router,
    pages_router,
)


class Application:
    def __init__(self) -> None:
        self.app = FastAPI(title=settings.app_name)
        self._mount_static()
        self._register_routers()
        self._create_tables()

    def _mount_static(self) -> None:
        self.app.mount("/static", StaticFiles(directory="app/static"), name="static")

    def _register_routers(self) -> None:
        self.app.include_router(health_router)
        self.app.include_router(dashboard_router)
        self.app.include_router(pages_router)
        self.app.include_router(category_router)
        self.app.include_router(expense_router)
        self.app.include_router(import_router)

    def _create_tables(self) -> None:
        Base.metadata.create_all(bind=database.engine)

    def get_app(self) -> FastAPI:
        return self.app


application = Application()
app = application.get_app()

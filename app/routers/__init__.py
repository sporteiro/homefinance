from app.routers.admin_router import admin_router
from app.routers.category_router import category_router
from app.routers.dashboard_router import dashboard_router
from app.routers.expense_router import expense_router
from app.routers.health_router import health_router
from app.routers.import_router import import_router
from app.routers.pages_router import pages_router

__all__ = [
    "admin_router",
    "category_router",
    "dashboard_router",
    "expense_router",
    "health_router",
    "import_router",
    "pages_router",
]

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.routers.dependencies import get_db
from app.schemas import CategoryCreate, CategoryRead, CategoryUpdate
from app.services import CategoryService


class CategoryRouter:
    def __init__(self) -> None:
        self.router = APIRouter(prefix="/api/categories", tags=["categories"])
        self._register_routes()

    def _register_routes(self) -> None:
        self.router.add_api_route(
            "/",
            self.list_categories,
            methods=["GET"],
            response_model=list[CategoryRead],
        )
        self.router.add_api_route(
            "/{category_id}",
            self.get_category,
            methods=["GET"],
            response_model=CategoryRead,
        )
        self.router.add_api_route(
            "/",
            self.create_category,
            methods=["POST"],
            response_model=CategoryRead,
            status_code=status.HTTP_201_CREATED,
        )
        self.router.add_api_route(
            "/{category_id}",
            self.update_category,
            methods=["PUT"],
            response_model=CategoryRead,
        )
        self.router.add_api_route(
            "/{category_id}",
            self.delete_category,
            methods=["DELETE"],
            status_code=status.HTTP_204_NO_CONTENT,
        )

    def list_categories(self, db: Session = Depends(get_db)) -> list[CategoryRead]:
        service = CategoryService(db)
        return service.list_all()

    def get_category(
        self, category_id: int, db: Session = Depends(get_db)
    ) -> CategoryRead:
        service = CategoryService(db)
        category = service.get_by_id(category_id)
        if category is None:
            raise HTTPException(status_code=404, detail="Category not found")
        return category

    def create_category(
        self, payload: CategoryCreate, db: Session = Depends(get_db)
    ) -> CategoryRead:
        service = CategoryService(db)
        if service.get_by_name(payload.name) is not None:
            raise HTTPException(status_code=409, detail="Category already exists")
        return service.create(payload)

    def update_category(
        self,
        category_id: int,
        payload: CategoryUpdate,
        db: Session = Depends(get_db),
    ) -> CategoryRead:
        service = CategoryService(db)
        category = service.update(category_id, payload)
        if category is None:
            raise HTTPException(status_code=404, detail="Category not found")
        return category

    def delete_category(
        self, category_id: int, db: Session = Depends(get_db)
    ) -> None:
        service = CategoryService(db)
        deleted = service.delete(category_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Category not found")


category_router = CategoryRouter().router

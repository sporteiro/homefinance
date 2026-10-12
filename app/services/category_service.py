from sqlalchemy.orm import Session

from app.models import Category
from app.schemas import CategoryCreate, CategoryUpdate


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

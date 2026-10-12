from app.core.constants import EXPENSE_TYPES
from app.core.database import database
from app.models import Category
from app.services import CategoryService

CATEGORY_DESCRIPTIONS = {
    "Electricity": "Power supply bills",
    "Water": "Water supply bills",
    "Internet": "Internet and connectivity bills",
    "Taxes": "Taxes and public fees",
    "Food": "Groceries and meals",
    "Car": "Fuel, tolls and car maintenance",
    "Travel": "Trips, flights and accommodation",
    "Other": "Uncategorized or miscellaneous",
}


class CategorySeeder:
    def __init__(self, session) -> None:
        self.session = session
        self.service = CategoryService(session)

    def run(self) -> int:
        created = 0
        for name in EXPENSE_TYPES:
            if self.service.get_by_name(name) is not None:
                continue
            category = Category(
                name=name,
                description=CATEGORY_DESCRIPTIONS.get(name),
            )
            self.session.add(category)
            created += 1
        self.session.commit()
        return created


def main() -> None:
    session = next(database.get_session())
    try:
        seeder = CategorySeeder(session)
        created = seeder.run()
        print(f"Seed complete. Categories created: {created}")
    finally:
        session.close()


if __name__ == "__main__":
    main()

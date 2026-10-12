from app.core.database import database
from app.models import Category
from app.services import CategoryService

DEFAULT_CATEGORIES = [
    ("Electricity", "Power supply bills"),
    ("Water", "Water supply bills"),
    ("Internet", "Internet and connectivity bills"),
    ("Food", "Groceries and meals"),
    ("Rent", "Housing rent or mortgage"),
    ("Transport", "Fuel, public transport, tolls"),
    ("Health", "Medical and pharmacy expenses"),
    ("Insurance", "Home, car and personal insurance"),
    ("Subscriptions", "Recurring digital services"),
    ("Other", "Uncategorized or miscellaneous"),
]


class CategorySeeder:
    def __init__(self, session) -> None:
        self.session = session
        self.service = CategoryService(session)

    def run(self) -> int:
        created = 0
        for name, description in DEFAULT_CATEGORIES:
            if self.service.get_by_name(name) is not None:
                continue
            category = Category(name=name, description=description)
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

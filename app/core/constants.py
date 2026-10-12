EXPENSE_TYPES: tuple[str, ...] = (
    "Electricity",
    "Water",
    "Internet",
    "Taxes",
    "Food",
    "Car",
    "Travel",
    "Other",
)


def is_valid_expense_type(name: str) -> bool:
    return name in EXPENSE_TYPES

import pytest

from app.schemas import CategoryCreate
from app.services import CategoryService


def test_create_and_fetch_category(session):
    service = CategoryService(session)

    category = service.create(CategoryCreate(name="Water"))

    assert category.id is not None
    assert service.get_by_name("Water") is not None


def test_get_or_create_is_idempotent(session):
    service = CategoryService(session)

    first = service.get_or_create("Electricity")
    second = service.get_or_create("Electricity")

    assert first.id == second.id

from datetime import date
from decimal import Decimal

from app.services.csv_parser import CsvParser


def test_parse_valid_row():
    content = "date,amount,description,category,id\n2024-01-15,42.50,Electricity bill,Electricity,abc123\n"
    parser = CsvParser()

    result = parser.parse(content)

    assert not result.errors
    assert len(result.rows) == 1
    row = result.rows[0]
    assert row.occurred_on == date(2024, 1, 15)
    assert row.amount == Decimal("42.50")
    assert row.description == "Electricity bill"
    assert row.category_name == "Electricity"
    assert row.external_id == "abc123"


def test_parse_supports_comma_decimal_separator():
    content = "date,amount,description,category,id\n15/01/2024,42,50,Water,Water,w1\n"
    parser = CsvParser(delimiter=";")

    result = parser.parse(content)

    assert not result.errors
    assert len(result.rows) == 1
    assert result.rows[0].amount == Decimal("42.50")


def test_parse_reports_errors():
    content = "date,amount,description,category,id\nnot-a-date,abc,Broken,Other,x1\n"
    parser = CsvParser()

    result = parser.parse(content)

    assert len(result.errors) == 1
    assert len(result.rows) == 0

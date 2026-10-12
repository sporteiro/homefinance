import csv
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from io import StringIO
from typing import Iterable


@dataclass
class ParsedRow:
    occurred_on: date
    amount: Decimal
    description: str | None
    category_name: str | None
    external_id: str | None
    raw: dict[str, str] = field(default_factory=dict)


@dataclass
class ParseError:
    line_number: int
    message: str


@dataclass
class ParseResult:
    rows: list[ParsedRow] = field(default_factory=list)
    errors: list[ParseError] = field(default_factory=list)


class CsvParser:
    DATE_FORMATS = ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d")

    def __init__(
        self,
        date_column: str = "date",
        amount_column: str = "amount",
        description_column: str = "description",
        category_column: str | None = "category",
        external_id_column: str | None = "id",
        delimiter: str = ",",
    ) -> None:
        self.date_column = date_column
        self.amount_column = amount_column
        self.description_column = description_column
        self.category_column = category_column
        self.external_id_column = external_id_column
        self.delimiter = delimiter

    def parse(self, content: str) -> ParseResult:
        result = ParseResult()
        reader = csv.DictReader(StringIO(content), delimiter=self.delimiter)

        if reader.fieldnames is None:
            result.errors.append(ParseError(0, "Empty or invalid CSV"))
            return result

        for index, raw_row in enumerate(reader, start=2):
            try:
                parsed = self._parse_row(raw_row)
                result.rows.append(parsed)
            except ValueError as error:
                result.errors.append(ParseError(index, str(error)))

        return result

    def _parse_row(self, raw_row: dict[str, str]) -> ParsedRow:
        occurred_on = self._parse_date(raw_row.get(self.date_column))
        amount = self._parse_amount(raw_row.get(self.amount_column))
        description = self._clean(raw_row.get(self.description_column))
        category_name = (
            self._clean(raw_row.get(self.category_column))
            if self.category_column
            else None
        )
        external_id = (
            self._clean(raw_row.get(self.external_id_column))
            if self.external_id_column
            else None
        )

        return ParsedRow(
            occurred_on=occurred_on,
            amount=amount,
            description=description,
            category_name=category_name,
            external_id=external_id,
            raw=raw_row,
        )

    def _parse_date(self, value: str | None) -> date:
        if not value:
            raise ValueError("Missing date value")

        cleaned = value.strip()
        for fmt in self.DATE_FORMATS:
            try:
                return datetime.strptime(cleaned, fmt).date()
            except ValueError:
                continue

        raise ValueError(f"Unsupported date format: {value!r}")

    def _parse_amount(self, value: str | None) -> Decimal:
        if value is None:
            raise ValueError("Missing amount value")

        cleaned = value.strip().replace(" ", "").replace(",", ".")
        if cleaned.startswith("+"):
            cleaned = cleaned[1:]

        try:
            return Decimal(cleaned)
        except InvalidOperation as error:
            raise ValueError(f"Invalid amount: {value!r}") from error

    def _clean(self, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

import csv
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from io import StringIO


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
    skipped: int = 0


class CsvParser:
    DATE_FORMATS = ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d")

    def __init__(
        self,
        date_column: str = "date",
        amount_column: str = "amount",
        description_column: str | None = "description",
        category_column: str | None = "category",
        external_id_column: str | None = "id",
        delimiter: str = ",",
        absolute_amount: bool = False,
        skip_positive: bool = False,
    ) -> None:
        self.date_column = date_column
        self.amount_column = amount_column
        self.description_column = self._normalize_column(description_column)
        self.category_column = self._normalize_column(category_column)
        self.external_id_column = self._normalize_column(external_id_column)
        self.delimiter = delimiter
        self.absolute_amount = absolute_amount
        self.skip_positive = skip_positive

    def parse(self, content: str) -> ParseResult:
        result = ParseResult()
        reader = csv.DictReader(StringIO(content), delimiter=self.delimiter)

        if reader.fieldnames is None:
            result.errors.append(ParseError(0, "Empty or invalid CSV"))
            return result

        for index, raw_row in enumerate(reader, start=2):
            try:
                amount = self._parse_amount(raw_row.get(self.amount_column))
            except ValueError as error:
                result.errors.append(ParseError(index, str(error)))
                continue

            if self.skip_positive and amount > 0:
                result.skipped += 1
                continue

            try:
                parsed = self._parse_row(raw_row, amount)
                result.rows.append(parsed)
            except ValueError as error:
                result.errors.append(ParseError(index, str(error)))

        return result

    def _parse_row(self, raw_row: dict[str, str], amount: Decimal) -> ParsedRow:
        occurred_on = self._parse_date(raw_row.get(self.date_column))
        normalized_amount = abs(amount) if self.absolute_amount else amount
        description = (
            self._clean(raw_row.get(self.description_column))
            if self.description_column
            else None
        )
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
            amount=normalized_amount,
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

        cleaned = value.strip().replace(" ", "")
        if not cleaned:
            raise ValueError("Empty amount value")

        cleaned = self._normalize_amount_string(cleaned)

        try:
            return Decimal(cleaned)
        except InvalidOperation as error:
            raise ValueError(f"Invalid amount: {value!r}") from error

    def _normalize_amount_string(self, value: str) -> str:
        # Handle thousands separators versus decimal separators.
        # Cases: "1234.56" (dot decimal), "1234,56" (comma decimal),
        # "1.234,56" (dot thousands, comma decimal), "1,234.56" (comma thousands, dot decimal).
        has_comma = "," in value
        has_dot = "." in value

        if has_comma and has_dot:
            if value.rfind(",") > value.rfind("."):
                # Format: 1.234,56 -> remove dots, replace comma with dot
                return value.replace(".", "").replace(",", ".")
            # Format: 1,234.56 -> remove commas
            return value.replace(",", "")

        if has_comma:
            return value.replace(",", ".")

        return value

    def _clean(self, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

    def _normalize_column(self, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

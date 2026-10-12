import hashlib

from sqlalchemy.orm import Session

from app.models import ImportBatch
from app.schemas import ExpenseCreate, ImportResult
from app.services.category_service import CategoryService
from app.services.csv_parser import CsvParser, ParsedRow
from app.services.expense_service import ExpenseService


class ImportService:
    DEFAULT_CATEGORY = "Other"

    def __init__(self, session: Session, parser: CsvParser | None = None) -> None:
        self.session = session
        self.parser = parser or CsvParser()
        self.category_service = CategoryService(session)
        self.expense_service = ExpenseService(session)

    def import_from_csv(
        self,
        filename: str,
        content: str,
        source: str,
        default_category_id: int | None = None,
    ) -> ImportResult:
        parse_result = self.parser.parse(content)

        rows_imported = 0
        rows_skipped = parse_result.skipped
        errors: list[str] = [
            f"line {error.line_number}: {error.message}"
            for error in parse_result.errors
        ]

        for parsed_row in parse_result.rows:
            external_id = self._resolve_external_id(parsed_row)

            if self.expense_service.exists_by_external_id(external_id):
                rows_skipped += 1
                continue

            category_id = self._resolve_category_id(
                parsed_row, default_category_id
            )

            if self.expense_service.exists_same_month_amount_category(
                category_id=category_id,
                occurred_on=parsed_row.occurred_on,
                amount=parsed_row.amount,
            ):
                rows_skipped += 1
                continue

            try:
                self._persist_row(
                    parsed_row, source, external_id, category_id
                )
                rows_imported += 1
            except Exception as error:
                rows_skipped += 1
                errors.append(f"row error: {error}")

        batch = ImportBatch(
            filename=filename,
            source=source,
            rows_total=(
                len(parse_result.rows)
                + len(parse_result.errors)
                + parse_result.skipped
            ),
            rows_imported=rows_imported,
            rows_skipped=rows_skipped,
        )
        self.session.add(batch)
        self.session.commit()

        return ImportResult(
            filename=filename,
            source=source,
            rows_total=batch.rows_total,
            rows_imported=rows_imported,
            rows_skipped=rows_skipped,
            errors=errors,
        )

    def _resolve_external_id(self, row: ParsedRow) -> str:
        if row.external_id:
            return row.external_id
        return self._fingerprint(row)

    def _fingerprint(self, row: ParsedRow) -> str:
        payload = (
            f"{row.occurred_on.isoformat()}|{row.amount}|{row.description or ''}"
        )
        digest = hashlib.sha1(payload.encode("utf-8")).hexdigest()
        return f"gen-{digest}"

    def _resolve_category_id(
        self,
        row: ParsedRow,
        default_category_id: int | None,
    ) -> int:
        if default_category_id is not None:
            return default_category_id

        name = row.category_name or self.DEFAULT_CATEGORY
        category = self.category_service.get_or_create(name)
        return category.id

    def _persist_row(
        self,
        row: ParsedRow,
        source: str,
        external_id: str,
        category_id: int,
    ) -> None:
        payload = ExpenseCreate(
            amount=row.amount,
            currency="EUR",
            description=row.description,
            occurred_on=row.occurred_on,
            source=source,
            external_id=external_id,
            category_id=category_id,
        )
        self.expense_service.create(payload)

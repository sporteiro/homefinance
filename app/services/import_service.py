from sqlalchemy.orm import Session

from app.models import ImportBatch
from app.schemas import ExpenseCreate, ImportResult
from app.services.category_service import CategoryService
from app.services.csv_parser import CsvParser, ParsedRow
from app.services.expense_service import ExpenseService


class ImportService:
    DEFAULT_CATEGORY = "Uncategorized"

    def __init__(self, session: Session, parser: CsvParser | None = None) -> None:
        self.session = session
        self.parser = parser or CsvParser()
        self.category_service = CategoryService(session)
        self.expense_service = ExpenseService(session)

    def import_from_csv(self, filename: str, content: str, source: str) -> ImportResult:
        parse_result = self.parser.parse(content)

        rows_imported = 0
        rows_skipped = 0
        errors: list[str] = [f"line {e.line_number}: {e.message}" for e in parse_result.errors]

        for parsed_row in parse_result.rows:
            if self._is_duplicate(parsed_row):
                rows_skipped += 1
                continue

            try:
                self._persist_row(parsed_row, source)
                rows_imported += 1
            except Exception as error:
                rows_skipped += 1
                errors.append(f"line ?: {error}")

        batch = ImportBatch(
            filename=filename,
            source=source,
            rows_total=len(parse_result.rows) + len(parse_result.errors),
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

    def _is_duplicate(self, row: ParsedRow) -> bool:
        if not row.external_id:
            return False
        return self.expense_service.exists_by_external_id(row.external_id)

    def _persist_row(self, row: ParsedRow, source: str) -> None:
        category = self.category_service.get_or_create(
            row.category_name or self.DEFAULT_CATEGORY
        )

        payload = ExpenseCreate(
            amount=row.amount,
            currency="EUR",
            description=row.description,
            occurred_on=row.occurred_on,
            source=source,
            external_id=row.external_id,
            category_id=category.id,
        )
        self.expense_service.create(payload)

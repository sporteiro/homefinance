import argparse
import sys
from pathlib import Path

from app.core.database import database
from app.services import CsvParser, ImportService


class CsvImportCommand:
    def __init__(self) -> None:
        self.parser = self._build_argument_parser()

    def _build_argument_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            description="Import expenses from a CSV file into HomeFinance."
        )
        parser.add_argument("file", type=Path, help="Path to the CSV file")
        parser.add_argument(
            "--source",
            default="bank",
            help="Source label for the import (default: bank)",
        )
        parser.add_argument("--date-column", default="date")
        parser.add_argument("--amount-column", default="amount")
        parser.add_argument("--description-column", default="description")
        parser.add_argument("--category-column", default="category")
        parser.add_argument("--external-id-column", default="id")
        parser.add_argument("--delimiter", default=",")
        return parser

    def run(self, argv: list[str]) -> int:
        args = self.parser.parse_args(argv)

        if not args.file.is_file():
            print(f"File not found: {args.file}", file=sys.stderr)
            return 1

        content = self._read_content(args.file)

        csv_parser = CsvParser(
            date_column=args.date_column,
            amount_column=args.amount_column,
            description_column=args.description_column,
            category_column=args.category_column or None,
            external_id_column=args.external_id_column or None,
            delimiter=args.delimiter,
        )

        session = next(database.get_session())
        try:
            service = ImportService(session, parser=csv_parser)
            result = service.import_from_csv(
                filename=args.file.name,
                content=content,
                source=args.source,
            )
        finally:
            session.close()

        self._print_result(result)
        return 0 if not result.errors else 2

    def _read_content(self, path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return path.read_text(encoding="latin-1")

    def _print_result(self, result) -> None:
        print(f"File: {result.filename}")
        print(f"Source: {result.source}")
        print(f"Rows total: {result.rows_total}")
        print(f"Rows imported: {result.rows_imported}")
        print(f"Rows skipped: {result.rows_skipped}")
        if result.errors:
            print("Errors:")
            for error in result.errors:
                print(f"  - {error}")


def main() -> None:
    command = CsvImportCommand()
    sys.exit(command.run(sys.argv[1:]))


if __name__ == "__main__":
    main()

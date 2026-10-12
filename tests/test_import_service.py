from app.services import CsvParser, ImportService


def test_import_csv_creates_expenses_and_batch(session):
    content = (
        "date,amount,description,category,id\n"
        "2024-01-10,15.75,Water bill,Water,w-001\n"
        "2024-01-11,60.00,Internet bill,Internet,i-001\n"
    )
    parser = CsvParser()
    service = ImportService(session, parser=parser)

    result = service.import_from_csv(
        filename="january.csv",
        content=content,
        source="bank",
    )

    assert result.rows_total == 2
    assert result.rows_imported == 2
    assert result.rows_skipped == 0
    assert not result.errors


def test_import_csv_skips_duplicates(session):
    content = (
        "date,amount,description,category,id\n"
        "2024-01-10,15.75,Water bill,Water,w-001\n"
    )
    parser = CsvParser()
    service = ImportService(session, parser=parser)

    first = service.import_from_csv("january.csv", content, "bank")
    second = service.import_from_csv("january.csv", content, "bank")

    assert first.rows_imported == 1
    assert second.rows_imported == 0
    assert second.rows_skipped == 1

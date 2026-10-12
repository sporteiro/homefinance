from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ImportBatchRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    source: str
    rows_total: int
    rows_imported: int
    rows_skipped: int
    created_at: datetime


class ImportResult(BaseModel):
    filename: str
    source: str
    rows_total: int
    rows_imported: int
    rows_skipped: int
    errors: list[str] = []

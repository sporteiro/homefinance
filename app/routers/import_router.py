from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.routers.dependencies import get_db
from app.schemas import ImportResult
from app.services import CsvParser, ImportService


class ImportRouter:
    def __init__(self) -> None:
        self.router = APIRouter(prefix="/api/imports", tags=["imports"])
        self._register_routes()

    def _register_routes(self) -> None:
        self.router.add_api_route(
            "/csv",
            self.import_csv,
            methods=["POST"],
            response_model=ImportResult,
            status_code=status.HTTP_201_CREATED,
        )

    async def import_csv(
        self,
        file: UploadFile = File(...),
        source: str = Form("bank"),
        date_column: str = Form("date"),
        amount_column: str = Form("amount"),
        description_column: str = Form("description"),
        category_column: str = Form("category"),
        external_id_column: str = Form("id"),
        delimiter: str = Form(","),
        db: Session = Depends(get_db),
    ) -> ImportResult:
        if not file.filename:
            raise HTTPException(status_code=400, detail="Missing filename")

        content_bytes = await file.read()
        try:
            content = content_bytes.decode("utf-8")
        except UnicodeDecodeError:
            content = content_bytes.decode("latin-1")

        parser = CsvParser(
            date_column=date_column,
            amount_column=amount_column,
            description_column=description_column,
            category_column=category_column or None,
            external_id_column=external_id_column or None,
            delimiter=delimiter,
        )

        service = ImportService(db, parser=parser)
        return service.import_from_csv(
            filename=file.filename,
            content=content,
            source=source,
        )


import_router = ImportRouter().router

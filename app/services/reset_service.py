from app.models import Expense, ImportBatch
from app.schemas import ResetRequest, ResetResult


class ResetService:
    CONFIRMATION_PHRASE = "RESET"

    def __init__(self, session) -> None:
        self.session = session

    def is_confirmation_valid(self, request: ResetRequest) -> bool:
        return request.confirmation == self.CONFIRMATION_PHRASE

    def reset(self, request: ResetRequest) -> ResetResult:
        deleted_expenses = 0
        deleted_imports = 0

        if request.scope in ("expenses", "all"):
            deleted_expenses = self._delete_expenses(request.category_id)

        if request.scope in ("imports", "all"):
            deleted_imports = self._delete_imports()

        self.session.commit()

        return ResetResult(
            scope=request.scope,
            category_id=request.category_id,
            deleted_expenses=deleted_expenses,
            deleted_imports=deleted_imports,
        )

    def _delete_expenses(self, category_id: int | None) -> int:
        query = self.session.query(Expense)
        if category_id is not None:
            query = query.filter(Expense.category_id == category_id)
        count = query.count()
        query.delete(synchronize_session=False)
        return count

    def _delete_imports(self) -> int:
        query = self.session.query(ImportBatch)
        count = query.count()
        query.delete(synchronize_session=False)
        return count

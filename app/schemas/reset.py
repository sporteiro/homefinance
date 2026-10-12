from typing import Literal

from pydantic import BaseModel, Field

ResetScope = Literal["expenses", "imports", "all"]


class ResetRequest(BaseModel):
    scope: ResetScope = Field(
        ...,
        description="What to reset: expenses, imports or all data.",
    )
    category_id: int | None = Field(
        default=None,
        description="If provided and scope is expenses, only that category is cleared.",
    )
    confirmation: str = Field(
        ...,
        description="Must match the confirmation phrase exactly.",
    )


class ResetResult(BaseModel):
    scope: ResetScope
    category_id: int | None
    deleted_expenses: int
    deleted_imports: int

from typing import Generator

from sqlalchemy.orm import Session

from app.core.database import database


def get_db() -> Generator[Session, None, None]:
    yield from database.get_session()

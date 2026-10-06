"""SQLite engine, session dependency, and table initialization."""

from collections.abc import Generator
from pathlib import Path

from sqlalchemy import event, inspect, text
from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings


def _ensure_sqlite_parent(database_url: str) -> None:
    prefix = "sqlite:///"
    if not database_url.startswith(prefix):
        return
    path = database_url.removeprefix(prefix)
    if path and path != ":memory:":
        Path(path).expanduser().parent.mkdir(parents=True, exist_ok=True)


_ensure_sqlite_parent(settings.database_url)
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)


@event.listens_for(Engine, "connect")
def _enable_sqlite_foreign_keys(dbapi_connection, connection_record) -> None:
    del connection_record
    if settings.database_url.startswith("sqlite"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def create_all() -> None:
    from app.modules.user import models  # noqa: F401

    SQLModel.metadata.create_all(engine)
    _add_missing_columns()


def _add_missing_columns() -> None:
    """create_all() never alters existing tables; add columns introduced after a database was created."""
    columns = {column["name"] for column in inspect(engine).get_columns("conversations")}
    if "project_id" not in columns:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE conversations ADD COLUMN project_id VARCHAR REFERENCES projects(id)"))
            connection.execute(text("CREATE INDEX IF NOT EXISTS ix_conversations_project_id ON conversations (project_id)"))

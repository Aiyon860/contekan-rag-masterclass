from collections.abc import Iterator

from sqlalchemy import event
from sqlmodel import Session, create_engine

from .config import config

config.data_dir.mkdir(parents=True, exist_ok=True)
config.uploads_dir.mkdir(parents=True, exist_ok=True)

engine = create_engine(config.db_url, connect_args={"check_same_thread": False})


@event.listens_for(engine, "connect")
def _fk_on(dbapi_conn, _):
    dbapi_conn.execute("PRAGMA foreign_keys=ON")


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session

from sqlmodel import create_engine, SQLModel, Session
from .config import settings

sqlite_url = f"sqlite:///{settings.db_path}"
engine = create_engine(sqlite_url, echo=True, connect_args={'check_same_thread': False})


def create_db():
    with Session(engine) as session:
        session.execute("PRAGMA foreign_keys=ON")
        SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
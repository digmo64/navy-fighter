import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session

os.makedirs("data", exist_ok=True)
DATABASE_URL = "sqlite:///data/navy_fighter.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

SessionFactory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
db_session = scoped_session(SessionFactory)
Base = declarative_base()


def init_db() -> None:
    from app.models import db_models  # noqa: F401
    Base.metadata.create_all(bind=engine)
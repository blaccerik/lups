from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

DATABASE_URL = f"postgresql://erik:erik@localhost:5432/testing"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_test_session() -> Session:
    return SessionLocal()


def get_test_postgres_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

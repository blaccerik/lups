from contextlib import contextmanager

from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = f"postgresql://{os.environ.get('POSTGRES_USER', 'erik')}:" \
               f"{os.environ.get('POSTGRES_PASSWORD', 'erik')}@" \
               f"{os.environ.get('POSTGRES_BROKER_URL', 'localhost:5432')}/" \
               f"{os.environ.get('POSTGRES_DATABASE', 'postgres')}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


@contextmanager
def get_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        print("close")
        session.close()


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

import logging
import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = f"postgresql://{os.environ.get('POSTGRES_USER', 'erik')}:" \
               f"{os.environ.get('POSTGRES_PASSWORD', 'erik')}@" \
               f"{os.environ.get('POSTGRES_BROKER_URL', 'localhost:5432')}/" \
               f"{os.environ.get('POSTGRES_DATABASE', 'postgres')}"
logger = logging.getLogger(__name__)
logger.info(DATABASE_URL)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency
def get_postgres_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

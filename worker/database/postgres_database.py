import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = f"postgresql://{os.environ.get('POSTGRES_USER', 'erik')}:" \
               f"{os.environ.get('POSTGRES_PASSWORD', 'erik')}@" \
               "postgres:5432/postgres"
print(DATABASE_URL)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

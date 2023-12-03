import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = f"postgresql://{os.environ.get('POSTGRES_USER', 'erik')}:" \
               f"{os.environ.get('POSTGRES_PASSWORD', 'erik')}@" \
               f"{os.environ.get('POSTGRES_BROKER_URL', 'localhost:5432')}/" \
               f"{os.environ.get('POSTGRES_DATABASE', 'postgres')}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# # Dependency to get the database session
# async def get_postgres():
#     db = database
#     try:
#         await db.connect()
#         yield db
#     finally:
#         await db.disconnect()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

import logging
import os
import platform

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

operating_system = platform.system()
HOST = "postgres"
if operating_system == 'Windows':
    HOST = "localhost"

DATABASE_URL = f"postgresql://{os.environ.get('POSTGRES_USER', 'erik')}:" \
               f"{os.environ.get('POSTGRES_PASSWORD', 'erik')}@" \
               f"{HOST}:5432/postgres"
logger.info(DATABASE_URL)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

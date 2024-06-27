from sqlalchemy import MetaData, create_engine

from database.models import DBNewsCategory
from database.postgres_database import engine, Base, SessionLocal


def create_test_db():
    import psycopg2
    from psycopg2 import sql
    from psycopg2.errors import DuplicateDatabase

    conn = psycopg2.connect(
        database="postgres",
        user='erik',
        password='erik',
        host='localhost',
        port='5432'
    )
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        db_name = "testing"
        cursor.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(db_name)))
    except DuplicateDatabase as d:
        print(d)
        pass
    print("start")
    db_metadata = MetaData()
    test_engine = create_engine("postgresql://erik:erik@localhost:5432/testing")
    db_metadata.reflect(bind=test_engine)
    with engine.connect() as conn2:
        db_metadata.drop_all(bind=test_engine)
    print("dropped")

    # Create all tables
    Base.metadata.create_all(test_engine)
    print("created")


if __name__ == '__main__':
    print("start")
    metadata = MetaData()
    metadata.reflect(bind=engine)
    with engine.connect() as conn:
        metadata.drop_all(bind=engine)
    print("dropped")

    # Create all tables
    Base.metadata.create_all(engine)
    print("created")

    postgres_client = SessionLocal()
    translate = {
        "top": "top",
        "business": "äri",
        "world": "maailm",
        "sports": "sport",
        "entertainment": "meelelahutus",
        "health": "tervis",
        "food": "toit",
        "other": "muu",
        "environment": "keskkond"
    }
    for i in translate.values():
        dbnc = postgres_client.query(DBNewsCategory).filter_by(name=i).first()
        if dbnc is None:
            cat = DBNewsCategory()
            cat.name = i
            postgres_client.add(cat)
    postgres_client.commit()
    postgres_client.close()
    print("done")

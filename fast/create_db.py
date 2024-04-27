from sqlalchemy import MetaData

from database.postgres_database import engine, Base, SessionLocal
from database.models import DBNewsCategory

if __name__ == '__main__':
    print("start")
    # Drop all tables
    Base.metadata.drop_all(engine)

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

import json
from typing import List

from fastapi import HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session

from database.models import DBFilter
from schemas.music_schema import Filter, FilterConfig


def read_filters_by_user(user_id: int, postgres_client: Session) -> List[Filter]:
    dbfs = postgres_client.query(DBFilter).filter(
        DBFilter.user_id == user_id
    ).all()

    result = []
    for dbf in dbfs:
        config_list = json.loads(dbf.config)
        f = Filter(
            id=dbf.id,
            name=dbf.name,
            config=[FilterConfig(**c) for c in config_list]
        )
        result.append(f)
    return result


def create_filters_by_user(user_id: int, f: Filter, postgres_client: Session):
    dbf = DBFilter()
    dbf.name = f.name
    dbf.user_id = user_id
    dbf.config = json.dumps([c.model_dump() for c in f.config])
    postgres_client.add(dbf)
    postgres_client.commit()


def update_filters_by_user(user_id: int, f: Filter, postgres_client: Session):
    dbf = postgres_client.query(DBFilter).filter(and_(
        DBFilter.user_id == user_id,
        DBFilter.id == f.id
    )).first()
    if dbf is None:
        raise HTTPException(status_code=404, detail="User doesn't have this filter")
    if f.delete:
        postgres_client.delete(dbf)
        postgres_client.commit()
        return
    else:
        dbf.name = f.name
        dbf.user_id = user_id
        dbf.config = json.dumps([c.model_dump() for c in f.config])
        postgres_client.add(dbf)
        postgres_client.commit()

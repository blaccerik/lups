from sqlalchemy.orm import Session

from models import models
from utils.schemas import Item


def create_user(db: Session, item: Item):
    db_item = models.Item(**item.model_dump())
    db.add(db_item)
    db.commit()
    return item
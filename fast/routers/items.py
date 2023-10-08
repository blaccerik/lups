from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from services.crud import create_user
from utils.database import get_db
from schemas.schemas import Item, ItemCreate

router = APIRouter(prefix="/api/items")


@router.post("/", response_model=Item)
async def create_user_endpoint(user: ItemCreate, db: Session = Depends(get_db)):
    db_item = create_user(db, user)
    return db_item

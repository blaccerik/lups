from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from utils.schemas import User
from utils.auth import get_current_user
from utils.database import get_db

router = APIRouter(prefix="/api/chat")


@router.get("/")
async def create_user_endpoint(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    print(current_user)
    return None

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from services.chat_service import read_user, read_chats_by_user, read_messages, create_message, delete_messages
from utils.schemas import User, MessagePost, Message
from utils.auth import get_current_user
from utils.database import get_db

router = APIRouter(prefix="/api/chat")


@router.get("/")
async def get_chats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = read_user(current_user, db)
    chats = read_chats_by_user(user_id, db)
    return chats


@router.get("/{chat_id}")
async def get_chat(chat_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = read_user(current_user, db)
    return read_messages(chat_id, user_id, db)


@router.post("/{chat_id}", response_model=Message)
async def post_chat(chat_id: int, message_post: MessagePost, current_user: User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    print(message_post)
    user_id = read_user(current_user, db)
    msg = create_message(message_post.message, chat_id, user_id, db)
    return msg


@router.delete("/{chat_id}", status_code=status.HTTP_200_OK)
async def delete_chat(chat_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = read_user(current_user, db)
    delete_messages(chat_id, user_id, db)
    return

from typing import List

from sqlalchemy import and_
from sqlalchemy.orm import Session

from database.models import DBMessage
from schemas.schemas import ChatMessage

MESSAGES_SIZE = 5


def get_chat_messages(chat_id: int, session: Session) -> List[ChatMessage]:
    messages = session.query(DBMessage).filter(and_(
        DBMessage.chat_id == chat_id,
        DBMessage.deleted == False
    )).all()[-MESSAGES_SIZE:]
    return [ChatMessage(text=m.text, owner=m.owner) for m in messages]

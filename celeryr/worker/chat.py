from sqlalchemy import and_

from worker.database import get_session, DBMessage

MESSAGES_SIZE = 5


def get_chat(chat_id):
    with get_session() as session:
        messages = session.query(DBMessage).filter(and_(
            DBMessage.chat_id == chat_id,
            DBMessage.deleted == False
        )).all()[-MESSAGES_SIZE:]
    return messages


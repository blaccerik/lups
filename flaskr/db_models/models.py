import logging
import os
from functools import wraps

from sqlalchemy import Integer, String, Column, ForeignKey, Enum, Boolean, ARRAY, Float
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

logger = logging.getLogger('waitress')
uri = f"postgresql://" \
      f"{os.environ.get('POSTGRE_USER', 'erik')}:" \
      f"{os.environ.get('POSTGRE_PASSWORD', 'erik')}@{os.environ.get('POSTGRE_BROKER_URL', 'localhost:5432')}/" \
      f"{os.environ.get('POSTGRE_DATABASE', 'erik_db')}"
logger.info(uri)

engine = create_engine(uri)
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

Base = declarative_base()

def with_session(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with Session() as session:
            kwargs['session'] = session
            return func(*args, **kwargs)
    return wrapper

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)

    # len is 20
    google_id = Column(String(25), nullable=False, unique=True)
    name = Column(String(50), nullable=False)

    def __repr__(self):
        return f"User(id={self.id}, name='{self.name}')"


class Chat(Base):
    __tablename__ = 'chats'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    deleted = Column(Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"Chat(id={self.id}, user_id={self.user_id})"


class MessageType(Enum):
    USER = 'user'
    BOT = 'bot'


class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey('chats.id'), nullable=False)
    message_ee = Column(String(255), nullable=False)
    message_en = Column(String(255), nullable=False)
    type = Column(Enum("user", "bot", name="message_type_enum"), nullable=False)
    deleted = Column(Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"Message(id={self.id}, chat_id={self.chat_id}, message='{self.message_ee}', type={self.type})"

class Sentence(Base):
    __tablename__ = 'sentences'
    id = Column(Integer, primary_key=True)
    text = Column(String(500), nullable=False)
    vector = Column(ARRAY(Float), nullable=False)

    def __lt__(self, other):
        return True

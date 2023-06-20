from sqlalchemy import Integer, String, Column, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

from run_server import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    password = Column(String(50), nullable=False)

    chats = relationship('Chat', backref='user')
    def __repr__(self):
        return f"User(id={self.id}, name='{self.name}', n='{self.password}')"

class Chat(Base):
    __tablename__ = 'chats'
    id = Column(Integer, primary_key=True)
    message = Column(String(50), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    user = relationship('User')

    def __repr__(self):
        return f"Chat(id={self.id}, user_id={self.user_id})"

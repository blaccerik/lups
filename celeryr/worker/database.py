import os
from contextlib import contextmanager

from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, Boolean, Enum, Text, Date, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

DATABASE_URL = f"postgresql://{os.environ.get('POSTGRES_USER', 'erik')}:" \
               f"{os.environ.get('POSTGRES_PASSWORD', 'erik')}@" \
               f"{os.environ.get('POSTGRES_BROKER_URL', 'localhost:5432')}/" \
               f"{os.environ.get('POSTGRES_DATABASE', 'postgres')}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


@contextmanager
def get_session():
    session = SessionLocal()
    try:
        yield session
    except Exception as e:
        session.rollback()
        raise e
    finally:
        print("close session")
        session.close()


class DBUser(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)

    # len is 20
    google_id = Column(String(25), nullable=False, unique=True)
    name = Column(String(100), nullable=False)

    def __repr__(self):
        return f"User(id={self.id}, name='{self.name}')"


class DBMessage(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey('chats.id'), nullable=False)
    message_ee = Column(String(100), nullable=False)
    message_en = Column(String(100), nullable=False)
    type = Column(Enum("user", "bot", name="message_type_enum"), nullable=False)
    deleted = Column(Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"Message(id={self.id}, chat_id={self.chat_id}, message='{self.message_ee}', type={self.type})"


class DBNews(Base):
    __tablename__ = 'news'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    title = Column(Text, nullable=False)
    text = Column(Text, nullable=False)
    date = Column(Date, default=func.current_date(), nullable=False)

    # Define a foreign key reference to the NewsCategory table
    category_id = Column(Integer, ForeignKey('news_categories.id'), nullable=False)

    category = relationship('DBNewsCategory', back_populates='news')
    extra = relationship('DBNewsExtra', back_populates='news')


class DBNewsExtra(Base):
    __tablename__ = 'news_extra'
    id = Column(Integer, ForeignKey('news.id'), primary_key=True)
    link = Column(String, nullable=False)
    creator = Column(String(100), nullable=False)
    article_id = Column(String(32), unique=True, nullable=False)

    news = relationship('DBNews', back_populates='extra')


class DBNewsCategory(Base):
    __tablename__ = 'news_categories'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    # Define a one-to-many relationship with News
    news = relationship('DBNews', back_populates='category')
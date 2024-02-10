import logging
import os
from functools import wraps

from sqlalchemy import Integer, String, Column, ForeignKey, Enum, Boolean, ARRAY, Float, Text, PrimaryKeyConstraint, \
    DateTime, func, Date
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, relationship

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('model')
uri = f"postgresql://" \
      f"{os.environ.get('POSTGRE_USER', 'erik')}:" \
      f"{os.environ.get('POSTGRE_PASSWORD', 'erik')}@{os.environ.get('POSTGRE_BROKER_URL', 'localhost:5432')}/" \
      f"{os.environ.get('POSTGRE_DATABASE', 'postgres')}"
logger.info(f"Database uri: {uri}")

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
    message_ee = Column(String(100), nullable=False)
    message_en = Column(String(100), nullable=False)
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


class News(Base):
    __tablename__ = 'news'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String(100), nullable=False)
    text = Column(Text, nullable=False)
    date = Column(Date, default=func.current_date(), nullable=False)

    # Define a foreign key reference to the NewsCategory table
    category_id = Column(Integer, ForeignKey('news_categories.id'), nullable=False)

    # Establish a many-to-one relationship with NewsCategory
    category = relationship('NewsCategory', back_populates='news')


class NewsCategory(Base):
    __tablename__ = 'news_categories'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    # Define a one-to-many relationship with News
    news = relationship('News', back_populates='category')


class Pixel(Base):
    __tablename__ = "pixel"

    x = Column(Integer, nullable=False)
    y = Column(Integer, nullable=False)
    color = Column(Enum("red", "green", "blue", "yellow", "purple", "orange", "black", "white", name="color_name"),
                   nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("x", "y"),
    )


def init_db():
    # Drop all tables
    Base.metadata.drop_all(engine)
    logger.info("dropped")
    # Create all tables
    Base.metadata.create_all(engine)
    logger.info("created")
    with Session() as session:
        # static data
        from services.place_service import SIZE
        for x in range(SIZE):
            for y in range(SIZE):
                p = Pixel()
                p.x = x
                p.y = y
                p.color = "white"
                session.add(p)
        session.commit()


def populate_db():
    with Session() as session:
        # dummy data
        u = User()
        u.name = "erik"
        u.google_id = "2321215345"
        u2 = User()
        u2.name = "erik2"
        u2.google_id = "232323214675475463"
        session.add_all([u, u2])
        session.commit()

        c = Chat()
        c.user_id = u.id
        c2 = Chat()
        c2.user_id = u.id
        c3 = Chat()
        c3.user_id = u2.id
        session.add_all([c, c2, c3])
        session.commit()

        m = Message()
        m.chat_id = c.id
        m.type = "user"
        m.message_ee = "er"
        m.message_en = "3"
        m2 = Message()
        m2.chat_id = c.id
        m2.type = "user"
        m2.message_ee = "er"
        m2.message_en = "3"
        m3 = Message()
        m3.chat_id = c2.id
        m3.type = "bot"
        m3.message_ee = "er"
        m3.message_en = "3"
        session.add_all([m, m2, m3])
        session.commit()

        nc1 = NewsCategory()
        nc1.name = "Majandus"
        nc1.icon_name = "business_center"
        nc2 = NewsCategory()
        nc2.name = "Maksud"
        nc2.icon_name = "euro_symbol"
        nc3 = NewsCategory()
        nc3.name = "Ehitus"
        nc3.icon_name = "build"
        nc4 = NewsCategory()
        nc4.name = "Tervisehoid"
        nc4.icon_name = "local_hospital"
        session.add_all([nc1, nc2, nc3, nc4])
        session.commit()

        for i in range(1000):
            n1 = News()
            n1.user_id = u.id
            n1.category_id = nc1.id
            n1.title = "Some text!!"
            n1.text = "This is some txt. This is some txt.This is some txt.This is some txt.This is some txt."
            session.add(n1)

            n2 = News()
            n2.user_id = u2.id
            n2.category_id = nc2.id
            n2.title = "Some text2!!"
            n2.text = "Super LONG TEXT. Super LONG TEXT.Super LONG TEXT.Super LONG TEXT.Super LONG TEXT.Super LONG TEXT."
            session.add(n2)

        session.commit()
    logger.info("updated")

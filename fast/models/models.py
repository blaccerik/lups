from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Boolean, PrimaryKeyConstraint, Date, Text, func, VARCHAR
from sqlalchemy.orm import relationship

from utils.database import Base, engine, SessionLocal


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)


class DBUser(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)

    # len is 20
    google_id = Column(String(25), nullable=False, unique=True)
    name = Column(String(100), nullable=False)

    def __repr__(self):
        return f"User(id={self.id}, name='{self.name}')"


class DBChat(Base):
    __tablename__ = 'chats'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    deleted = Column(Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"Chat(id={self.id}, user_id={self.user_id})"


class DBMessage(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey('chats.id'), nullable=False)
    text = Column(String(512), nullable=False)
    text_model = Column(String(512), nullable=False)
    language = Column(Enum("estonia", "english", name="message_language_enum"), nullable=False)
    owner = Column(Enum("user", "model", name="message_owner_enum"), nullable=False)
    deleted = Column(Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"Message(id={self.id}, chat_id={self.chat_id}, message='{self.text}')"


class DBPixel(Base):
    __tablename__ = "pixel"

    x = Column(Integer, nullable=False)
    y = Column(Integer, nullable=False)
    color = Column(Enum("red", "green", "blue", "yellow", "purple", "orange", "black", "white", name="color_name"),
                   nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("x", "y"),
    )


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


def init_db():
    print("start")
    # Drop all tables
    Base.metadata.drop_all(engine)
    print("dropped")
    # Create all tables
    Base.metadata.create_all(engine)
    print("created")

    postgres_client = SessionLocal()

    # static data
    from services.place_service import SIZE
    for x in range(SIZE):
        for y in range(SIZE):
            p = DBPixel()
            p.x = x
            p.y = y
            p.color = "white"
            postgres_client.add(p)
    postgres_client.commit()

    translate = {
        "top": "top",
        "business": "äri",
        "world": "maailm",
        "sports": "sport",
        "entertainment": "meelelahutus",
        "health": "tervis",
        "food": "toit",
        "other": "muu",
        "environment": "keskkond"
    }
    for i in translate.values():
        cat = DBNewsCategory()
        cat.name = i
        postgres_client.add(cat)
    postgres_client.commit()

    postgres_client.close()
    print("done")

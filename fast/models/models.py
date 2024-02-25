from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Boolean, Date, Text, func
from sqlalchemy.orm import relationship

from utils.database import Base, engine, SessionLocal


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
    title = Column(String(100), unique=False)
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


class DBFamilyFeudGame(Base):
    __tablename__ = 'family_feud_game'
    code = Column(String(4), primary_key=True)
    auth = Column(String(4), nullable=True)
    started = Column(Boolean, nullable=False, default=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

class DBFamilyFeudRound(Base):
    __tablename__ = 'family_feud_round'
    id = Column(Integer, primary_key=True)
    game_code = Column(String(4), ForeignKey('family_feud_game.code', ondelete="CASCADE"), nullable=False)
    question = Column(String(25), nullable=False)
    round_number = Column(Integer, nullable=False)

    def __repr__(self):
        return f'{self.game_code} {self.id} {str(self.round_number)} {self.question}'

class DBFamilyFeudAnswer(Base):
    __tablename__ = 'family_feud_answer'
    id = Column(Integer, primary_key=True)
    round_id = Column(Integer, ForeignKey('family_feud_round.id', ondelete="CASCADE"), nullable=False)
    text = Column(String(25), nullable=False)
    points = Column(Integer, nullable=False)

    def __repr__(self):
        return f'{self.round_id} {self.text} {self.points}'



def init_db():

    print("start")
    # Drop all tables
    Base.metadata.drop_all(engine)

    print("dropped")
    # Create all tables
    Base.metadata.create_all(engine)
    print("created")

    postgres_client = SessionLocal()

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

    # u = DBUser(google_id="erik", name="erik")
    # postgres_client.add(u)
    # postgres_client.commit()
    #
    # f = DBFamilyFeudGame(code="erik", auth="erik", user_id=u.id)
    # postgres_client.add(f)
    # f2 = DBFamilyFeudGame(code="eri2", auth="erik", user_id=u.id)
    # postgres_client.add(f2)
    # postgres_client.commit()
    #
    # r1 = DBFamilyFeudRound(code=f.code, round_number=1, text="tere", points=1)
    # postgres_client.add(r1)
    # postgres_client.commit()
    #
    # r2 = DBFamilyFeudRound(code=f.code, round_number=2, text="tere", points=1)
    # postgres_client.add(r2)
    # postgres_client.commit()
    #
    # r3 = DBFamilyFeudRound(code=f2.code, round_number=1, text="tere", points=1)
    # postgres_client.add(r3)
    # postgres_client.commit()
    #
    # r4 = DBFamilyFeudRound(code=f2.code, round_number=2, text="tere", points=1)
    # postgres_client.add(r4)
    # postgres_client.commit()

    postgres_client.close()
    print("done")

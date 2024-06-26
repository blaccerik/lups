from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Boolean, Date, Text, func, DateTime, Float
from sqlalchemy.orm import relationship

from database.postgres_database import Base


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
    language = Column(Enum("estonia", "english", name="message_language_enum"), nullable=False)
    owner = Column(String(10), nullable=False)
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
    question = Column(String(40), nullable=False)
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


class DBArtist(Base):
    __tablename__ = "artist"
    # channel id is 24
    id = Column(String(24), primary_key=True)
    name = Column(String(100), nullable=False)


class DBSong(Base):
    __tablename__ = 'song'
    # video url seems to be 11 chars long
    id = Column(String(11), primary_key=True)
    status = Column(Enum("ready", "working", "idle", name="status"), nullable=False)
    date = Column(DateTime, nullable=False, default=func.now())
    title = Column(String(100), nullable=True)
    length = Column(Integer, nullable=True)
    artist_id = Column(String(24), ForeignKey('artist.id'), nullable=True)
    # OMV: Original Music Video - uploaded by original artist with actual video content
    # UGC: User Generated Content - uploaded by regular YouTube user
    # ATV: High quality song uploaded by original artist with cover image
    # OFFICIAL_SOURCE_MUSIC: Official video content, but not for a single track
    type = Column(Enum(
        'MUSIC_VIDEO_TYPE_UGC',
        'MUSIC_VIDEO_TYPE_ATV',
        'MUSIC_VIDEO_TYPE_OMV',
        'OFFICIAL_SOURCE_MUSIC',
        'MUSIC_VIDEO_TYPE_PODCAST_EPISODE',
        name='song_type'), nullable=True)

    def __repr__(self):
        return f"Song({self.id})"


class DBReaction(Base):
    __tablename__ = "reaction"
    song_id = Column(String(11), ForeignKey("song.id", ondelete='CASCADE'), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    date = Column(DateTime, nullable=False, default=func.now())
    liked = Column(Boolean, nullable=False)
    # how long user listened the song for
    duration = Column(Integer, nullable=False)

    def __repr__(self):
        return f"React({self.user_id})"


class DBSongRelationV2(Base):
    __tablename__ = "song_relation_v2"
    id = Column(String(22), primary_key=True)
    date = Column(DateTime, nullable=False, default=func.now())
    distance = Column(Float, nullable=False, default=1.0)

    def __repr__(self):
        return f"Rel({self.id})"


class DBFilter(Base):
    __tablename__ = "filter"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    config = Column(Text, nullable=False)


class DBSongQueue(Base):
    __tablename__ = "song_queue"
    song_id = Column(String(11), ForeignKey("song.id", ondelete='CASCADE'), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    song_nr = Column(Integer, nullable=False)
    hidden = Column(Boolean, nullable=False, default=False)

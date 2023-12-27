from enum import Enum

from pydantic import BaseModel


class Item(BaseModel):
    name: str


class ItemCreate(Item):
    pass


class User(BaseModel):
    google_id: str
    name: str


class AIModelType(Enum):
    small = "small"  # TheBloke/TinyLlama-1.1B-1T-OpenOrca-GGUF


class LanguageType(Enum):
    estonia = "estonia"
    english = "english"


class MessageOwner(Enum):
    user = "user"
    model = "model"


class InputType(Enum):
    cancel = "cancel"
    delete = "delete"
    message = "message"

class ChatUpdate(BaseModel):
    title: str

class ChatRespond(BaseModel):
    title: str
    chat_id: int


class ChatPost(BaseModel):
    type: InputType
    ai_model_type: AIModelType
    language_type: LanguageType
    message_text: str
    message_id: int


class ChatPostRespond(BaseModel):
    stream_id: str
    message_id: int


class Message(BaseModel):
    message_id: int
    message_text: str
    message_owner: MessageOwner
    language_type: LanguageType


class News(BaseModel):
    creator_id: str | None
    creator: str
    id: int
    title: str
    date: str
    text: str
    category: str
    has_image: bool
    link: str | None


class NewsId(BaseModel):
    id: int


class PixelSmall(BaseModel):
    x: int
    y: int
    c: int


class PixelLarge(BaseModel):
    x: int
    y: int
    color: str

from enum import Enum

from pydantic import BaseModel, constr


class Chat(BaseModel):
    title: str
    chat_id: int


class ChatUpdate(BaseModel):
    title: constr(min_length=1, max_length=100)


class ChatPostRespond(BaseModel):
    stream_id: str
    message_id: int


class LanguageType(Enum):
    estonia = "estonia"
    english = "english"


class OwnerType(Enum):
    user = "user"
    small = "small"


class ChatMessage(BaseModel):
    id: int
    text: constr(min_length=1, max_length=512)
    owner: OwnerType
    language: LanguageType

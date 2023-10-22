from enum import Enum

from pydantic import BaseModel


class Item(BaseModel):
    name: str


class ItemCreate(Item):
    pass


class User(BaseModel):
    google_id: str
    name: str


class MessageType(str, Enum):
    user = "user"
    bot = "bot"


class Message(BaseModel):
    id: int
    message: str
    type: MessageType


class MessagePost(BaseModel):
    message: str


class News(BaseModel):
    user_id: int
    title: str
    text: str
    category: str


class Pixel(BaseModel):
    x: int
    y: int
    c: int

from enum import Enum

from fastapi import UploadFile
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
from enum import Enum
from typing import Union, List

from pydantic import BaseModel, Field


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


# place schemas
class PlaceColor(str, Enum):
    red = "red"
    green = "green"
    blue = "blue"
    yellow = "yellow"
    purple = "purple"
    orange = "orange"
    black = "black"
    white = "white"


class PlaceInput(BaseModel):
    tool: str
    x: int = Field(ge=0, lt=300)
    y: int = Field(ge=0, lt=300)
    size: int = Field(gt=0, le=20)
    matrix: List[List[Union[PlaceColor, None]]]

    @staticmethod
    def validate_matrix_size(matrix, size):
        if len(matrix) != size:
            raise ValueError("Matrix size does not match the specified 'size'")
        for row in matrix:
            if len(row) != size:
                raise ValueError("Each row in the matrix must have the specified 'size'")


class PlacePixel(BaseModel):
    color: PlaceColor
    user: str | None


class PlaceOutput(BaseModel):
    c: str  # must be str instead PlaceColor for faster send
    u: str | None
    x: int
    y: int

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


class OutputType(Enum):
    error = "error"
    data = "data"
    message = "message"
    stream_message = "stream_message"
    completed = "completed"



class InputType(Enum):
    cancel = "cancel"
    delete = "delete"
    message = "message"


class ChatInput(BaseModel):
    type: InputType
    ai_model_type: AIModelType
    language_type: LanguageType
    message_text: str
    message_id: int


class ChatOutput(BaseModel):
    type: OutputType


class ChatOutputData(ChatOutput):
    queue_number: int


class ChatOutputError(ChatOutput):
    message_text: str


class ChatOutputMessage(ChatOutput):
    message_id: int
    message_text: str
    message_owner: MessageOwner
    language_type: LanguageType


class Message(BaseModel):
    message_id: int
    message_text: str
    message_owner: MessageOwner
    language_type: LanguageType


class MessageSend(Message):
    part: int  # set to -1 if message is complete. else shows message part number


class MessageReceive(BaseModel):
    text: str


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

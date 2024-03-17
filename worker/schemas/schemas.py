from enum import Enum

from pydantic import BaseModel


class ChatOwner(str, Enum):
    user = "user"
    model = "model"


class ChatMessage(BaseModel):
    text_model: str
    owner: ChatOwner

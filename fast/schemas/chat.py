from enum import Enum

from pydantic import BaseModel, constr

# class InputType(Enum):
#     cancel = "cancel"
#     delete = "delete"
#     message = "message"



class Chat(BaseModel):
    title: str
    chat_id: int

class ChatUpdate(BaseModel):
    title: constr(min_length=1, max_length=100)





# class ChatPost(BaseModel):
#     ai_model_type: AIModelType
#     language: LanguageType
#     text: str
#     id: int


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

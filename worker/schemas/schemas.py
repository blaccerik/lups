from pydantic import BaseModel


class ChatMessage(BaseModel):
    text: str
    owner: str

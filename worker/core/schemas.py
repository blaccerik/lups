from pydantic import BaseModel

class Message(BaseModel):
    owner: str
    text: str
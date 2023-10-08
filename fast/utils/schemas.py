from pydantic import BaseModel

class Item(BaseModel):
    name: str

class ItemCreate(Item):
    pass

class User(BaseModel):
    google_id: str
    name: str
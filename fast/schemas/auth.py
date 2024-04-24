from pydantic import BaseModel


class User(BaseModel):
    google_id: str
    name: str


class UserExtra(BaseModel):
    google_id: str
    name: str
    user_id: int

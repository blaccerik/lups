from typing import List

from pydantic import BaseModel


class Answer(BaseModel):
    text: str
    points: int


class GameRoundData(BaseModel):
    current: int
    total: int
    answers: List[Answer]


class Game(BaseModel):
    code: str
    auth: str | None


class GameRound(BaseModel):
    answers: List[Answer]
    round_number: int
    question: str


class GameData(BaseModel):
    rounds: List[GameRound]


# class GameReceiveData(BaseModel):
#     round_number: int
#     question: Question

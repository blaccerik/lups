from typing import List

from pydantic import BaseModel, constr, conint


class Answer(BaseModel):
    text: constr(min_length=1, max_length=25)
    points: conint(ge=1, le=100)


# class GameRoundData(BaseModel):
#     current: int
#     total: int
#     answers: List[Answer]


class Game(BaseModel):
    code: str
    started: bool
    auth: str


class GameRound(BaseModel):
    answers: List[Answer]
    round_number: int
    question: constr(min_length=1, max_length=20)


class GameData(BaseModel):
    rounds: List[GameRound]
    started: bool
    code: str
    auth: str


class GameStatus(BaseModel):
    started: bool

# class GameReceiveData(BaseModel):
#     round_number: int
#     question: Question

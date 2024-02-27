from typing import List

from pydantic import BaseModel, constr, conint


class Answer(BaseModel):
    text: constr(min_length=1, max_length=25)
    points: conint(ge=1, le=100)


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
    question: constr(min_length=1, max_length=20)

class Code(BaseModel):
    code: constr(min_length=4, max_length=4)

class GameData(BaseModel):
    rounds: List[GameRound]


# class GameReceiveData(BaseModel):
#     round_number: int
#     question: Question

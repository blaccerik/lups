import logging
import random
import string
from typing import List

from fastapi import HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session

from models.models import DBFamilyFeudGame, DBUser, DBFamilyFeudQuestion
from schemas.familyfeud import Game, Answer, GameRound
from utils.schemas import User
logger = logging.getLogger("FamilyService")

def read_games_by_user(user_id: int, session: Session):
    games = session.query(DBFamilyFeudGame).filter(
        DBFamilyFeudGame.user_id == user_id
    ).all()
    return [Game(auth=g.auth, code=g.code) for g in games]


def create_game_by_user(user_id: int, session: Session):
    letters = string.ascii_lowercase
    for _ in range(3):
        code = ''.join(random.choice(letters) for _ in range(4))
        # check if code is valid
        g = session.query(DBFamilyFeudGame).get(code)
        logger.info(f"Generated code: {code} database: {g}")
        if not g:
            break
    else:
        raise HTTPException(status_code=400, detail="No codes left")

    auth = ''.join(random.choice(letters) for _ in range(4))
    ffg = DBFamilyFeudGame(code=code, auth=auth, user_id=user_id)
    session.add(ffg)
    session.commit()
    return Game(auth=auth, code=code)


def user_has_game(code: str, user_id: int, session: Session):
    game = session.query(DBFamilyFeudGame).filter(and_(
        DBFamilyFeudGame.code == code,
        DBFamilyFeudGame.user_id == user_id
    ))
    if not game:
        raise HTTPException(status_code=403, detail="User does not have that game")

def read_game(code: str, user_id: int, session: Session):
    # user_has_game(code, user_id, session)
    # rounds = session.query(DBFamilyFeudQuestion).filter(DBFamilyFeudQuestion.code == code).all()
    # groups = {}
    # for r in rounds:
    #     nr = r.round_number
    #     q = Question(text=r.text, points=r.points)
    #     if nr in groups:
    #         groups[nr].append(q)
    #     else:
    #         groups[nr] = [q]
    groups = {
        1: [
            Answer(text="question 11", points=50),
            Answer(text="question 12", points=50),
        ],
        2: [
            Answer(text="question 21", points=26),
            Answer(text="question 22", points=25),
            Answer(text="question 23", points=25),
            Answer(text="question 24", points=25),
        ],
        3: [
            Answer(text="question 31", points=60),
            Answer(text="question 32", points=40),
        ],
        4: [
            Answer(text="question 41", points=25),
            Answer(text="question 42", points=25),
            Answer(text="question 43", points=25),
            Answer(text="question 44", points=25),
        ]

    }
    return [GameRound(answers=q, round_number=k, question="dummy text?") for k, q in groups.items()]


def create_game_data(code: str, data: List[GameRound], user_id: int, session: Session):
    user_has_game(code, user_id, session)
    for d in data:
        ffq = DBFamilyFeudQuestion(code=code, round_number=d.round_number, text=d.question.text, points=d.question.points)
        session.add(ffq)
    session.commit()

def start_game_by_user(code: str, user_id: int, session: Session):
    game = read_game(code, user_id, session)

    # check if points match
    for game_round in game:
        total = 0
        for question in game_round.answers:
            total += question.points
        if total != 100:
            raise HTTPException(status_code=400, detail="Round does not have 100 points")





import logging
import random
import string
from typing import List

from fastapi import HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session

from models.models import DBFamilyFeudGame, DBUser, DBFamilyFeudAnswer, DBFamilyFeudRound
from schemas.familyfeud import Game, Answer, GameRound, Code
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
    )).first()
    if not game:
        raise HTTPException(status_code=403, detail="User does not have that game")

def read_game(code: str, user_id: int, session: Session):
    user_has_game(code, user_id, session)

    # get results
    results = session.query(DBFamilyFeudRound, DBFamilyFeudAnswer).filter(and_(
        DBFamilyFeudRound.game_code == code,
        DBFamilyFeudAnswer.round_id == DBFamilyFeudRound.id
    )).all()

    # group answers to rounds
    data = {}
    for db_r, db_a in results:
        a = Answer(text=db_a.text, points=db_a.points)
        if db_r.id in data:
            data[db_r.id].answers.append(a)
        else:
            data[db_r.id] = GameRound(round_number=db_r.round_number, question=db_r.question, answers=[a])
    return [r for r in data.values()]


def create_game_data(code: str, rounds: List[GameRound], user_id: int, session: Session):

    MAX_ROUNDS = 10
    MAX_ANSWERS = 10

    # validate data
    if len(rounds) == 0 or len(rounds) > MAX_ROUNDS:
        raise HTTPException(status_code=400, detail="Data out of bounds")
    for r in rounds:
        if len(r.answers) == 0 or len(r.answers) > MAX_ANSWERS:
            raise HTTPException(status_code=400, detail="Data out of bounds")
        points = 0
        for a in r.answers:
            points += a.points
        if points != 100:
            raise HTTPException(status_code=400, detail="Data out of bounds")

    # check if game exists
    user_has_game(code, user_id, session)

    # Delete all rows with the specified code
    session.query(DBFamilyFeudRound).filter(DBFamilyFeudRound.game_code == code).delete()
    session.commit()

    # add new data
    for r_index in range(len(rounds)):
        r = rounds[r_index]
        ffr = DBFamilyFeudRound(round_number=r_index + 1, question=r.question, game_code=code)
        session.add(ffr)
        session.flush()
        for a in r.answers:
            ffa = DBFamilyFeudAnswer(round_id=ffr.id, text=a.text, points=a.points)
            session.add(ffa)
    session.commit()


    # # check if user has that game
    # user_has_game(code, user_id, session)
    #
    # for d in rounds:
    #     ffq = DBFamilyFeudQuestion(code=code, round_number=d.round_number, text=d.question.text, points=d.question.points)
    #     session.add(ffq)
    # session.commit()

def start_game_by_user(code: str, user_id: int, session: Session):
    game = read_game(code, user_id, session)

    # check if points match
    for game_round in game:
        total = 0
        for question in game_round.answers:
            total += question.points
        if total != 100:
            raise HTTPException(status_code=400, detail="Round does not have 100 points")





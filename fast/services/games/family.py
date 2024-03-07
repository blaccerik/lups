import logging
import random
import string
from typing import List

from fastapi import HTTPException
from redis.client import Redis
from sqlalchemy import and_
from sqlalchemy.orm import Session

from models.models import DBFamilyFeudGame, DBFamilyFeudAnswer, DBFamilyFeudRound
from schemas.familyfeud import Game, Answer, GameRound, GameData, GameStatus, LiveGame, LiveGameType, LiveGameAnswer

logger = logging.getLogger("FamilyService")


def read_games_by_user(user_id: int, session: Session):
    games = session.query(DBFamilyFeudGame).filter(
        DBFamilyFeudGame.user_id == user_id
    ).all()
    return [Game(auth=g.auth, code=g.code, started=g.started) for g in games]


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
    return Game(auth=auth, code=code, started=False)


def user_has_game(code: str, user_id: int, session: Session):
    game = session.query(DBFamilyFeudGame).filter(and_(
        DBFamilyFeudGame.code == code,
        DBFamilyFeudGame.user_id == user_id
    )).first()
    if not game:
        raise HTTPException(status_code=403, detail="User does not have that game")
    return game


def read_game(code: str, user_id: int, session: Session) -> GameData:
    game = user_has_game(code, user_id, session)

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
    rounds = list(data.values())
    for r in rounds:
        r.answers.sort(key=lambda x: x.points, reverse=True)

    return GameData(
        rounds=rounds,
        started=game.started,
        code=game.code,
        auth=game.auth
    )


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


async def set_game_status(code: str, user_id: int, game_status: GameStatus, session: Session, redis_client: Redis):
    game = user_has_game(code, user_id, session)
    game.started = game_status.started
    session.add(game)
    session.commit()

    # add first round to redis
    if game_status.started:
        game_data = read_game(code, user_id, session)
        first_round = game_data.rounds[0]
        answers = [
            LiveGameAnswer(text=answer.text, points=answer.points, revealed=False) for answer in first_round.answers]
        lg = LiveGame(
            type=LiveGameType.game,
            answers=answers,
            number=first_round.round_number,
            question=first_round.question,
            strikes=0
        )
        await redis_client.hset("games", code, lg.model_dump_json())
    return Game(auth=game.auth, code=game.code, started=game.started)


def read_game_by_code(code: str, session: Session):
    game = session.query(DBFamilyFeudGame).get(code)
    return game

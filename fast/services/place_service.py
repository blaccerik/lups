from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from models.models import DBPixel

SIZE = 300
COLORS = [
    "red", "green", "blue", "yellow", "purple", "orange", "black", "white"
]


def read_pixels(session: Session):
    pixels = session.query(DBPixel).all()
    return [{
        "x": p.x,
        "y": p.y,
        "c": COLORS.index(p.color)
    } for p in pixels]


def edit_pixel(x, y, color, session: Session):
    if x < 0 or x >= SIZE:
        return False
    elif y < 0 or y >= SIZE:
        return False
    elif color not in COLORS:
        return False
    try:
        pixel = session.query(DBPixel).filter_by(x=x, y=y).one()
        pixel.color = color
        session.commit()
        return True
    except NoResultFound:
        return False

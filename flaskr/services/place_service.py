from sqlalchemy.exc import NoResultFound

from db_models.models import Pixel, with_session

SIZE = 300
COLORS = [
    "red", "green", "blue", "yellow", "purple", "orange", "black", "white"
]


@with_session
def get_pixels(session=None):
    pixels = session.query(Pixel).all()
    return [{
        "x": p.x,
        "y": p.y,
        "color": p.color
    } for p in pixels]


@with_session
def edit_pixel(x, y, color, google_id: int, session=None):
    if x < 0 or x >= SIZE:
        return False
    elif y < 0 or y >= SIZE:
        return False
    elif color not in COLORS:
        return False
    try:
        pixel = session.query(Pixel).filter_by(x=x, y=y).one()
        pixel.color = color
        session.commit()
        return True
    except NoResultFound:
        return False

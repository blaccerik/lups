from flask import Blueprint

from db_models.models import User
from run_server import db_session

bp = Blueprint('test', __name__, url_prefix="/test")

@bp.route('', methods=['GET'])
def test():
    print(db_session.query(User).all())
    return "hi"
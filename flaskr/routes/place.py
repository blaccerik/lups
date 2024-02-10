from flask import Blueprint, jsonify

from services.place_service import get_pixels
from shared import logger

bp = Blueprint('place', __name__, url_prefix="/place")


@bp.route("", methods=['GET'])
def get_all_pixels():
    logger.info("get pixels")
    data = get_pixels()
    logger.info(len(data))
    return jsonify(data), 200

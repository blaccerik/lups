from flask import Blueprint, jsonify
from flask_socketio import SocketIO, emit

from routes.test import token_required
from services.place_service import get_pixels, edit_pixel
from shared import logger

socketio = SocketIO(async_mode='eventlet', cors_allowed_origins="*")
bp = Blueprint('place', __name__, url_prefix="/place")


@bp.route("", methods=['GET'])
def get_all_pixels():
    logger.info("get pixels")

    data = get_pixels()
    logger.info(len(data))
    logger.info(data[0])
    return jsonify(data), 200

# @socketio.on('connect', namespace="/place")
# def handle_connect():
#     data = get_pixels()
#     print('WebSocket client connected')
#     # data = {
#     #     "hi": 4
#     # }
#     # print(data)
#     emit("init", data)


# Define a custom WebSocket event handler for a custom event
@socketio.on('update', namespace="/place")
@token_required
def handle_my_event(data, google_id, name):
    x = data["x"]
    y = data["y"]
    color = data["color"]
    logger.info(f"edit {data}")
    response = edit_pixel(x, y, color, google_id)
    logger.info(response)
    if response:
        emit('update_response', data, broadcast=True)
    else:
        emit('update_response', "error")

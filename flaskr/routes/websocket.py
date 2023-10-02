import logging

from flask_socketio import SocketIO, emit

from routes.test import token_required
from services.place_service import edit_pixel
from shared import logger

loggerws = logging.getLogger("websocket")
loggerws.info("weboscketere")
socketio = SocketIO(async_mode='eventlet', cors_allowed_origins=[
    "http://localhost:63342/"
])

# Define a custom WebSocket event handler for a custom event
@socketio.on('update', namespace="/ws/place")
def handle_my_event(data):
    loggerws.info(data)
    x = data["x"]
    y = data["y"]
    color = data["color"]
    logger.info(f"edit {data}")
    # response = edit_pixel(x, y, color, google_id)
    response = True
    logger.info(response)
    if response:
        emit('update_response', data, broadcast=True)
    else:
        emit('update_response', "error")

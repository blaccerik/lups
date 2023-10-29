import socketio

import logging

# comment/edit line 5 if you don't want use redis or using other message queue
# see https://python-socketio.readthedocs.io/en/latest/server.html#using-a-message-queue
# mgr = socketio.AsyncRedisManager(url="redis://localhost:6379/0")

# sio = socketio.AsyncServer(
#     logger=True,
#     async_mode="asgi", cors_allowed_origins=["*", "http://localhost:4200"] #, client_manager=mgr
# )
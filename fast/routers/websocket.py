import asyncio
import json
from typing import Any

from aioredis_fastapi import (
    get_session,
)
from fastapi import APIRouter, WebSocket, Depends, WebSocketDisconnect
from sqlalchemy.orm import Session

from utils.database import get_db

router = APIRouter(prefix="/api/websocket")


# Create a list to store connected websockets
connected_clients = []

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()

    # Add the websocket to the list of connected clients
    connected_clients.append(websocket)
    print("new", websocket)
    message = {"message": "Hello"}
    j = json.dumps(message)

    await websocket.send_text(j)
    try:
        while True:
            data = await websocket.receive_text()
            print(data)
            # You can add your database operations here if needed
            # items = db.query(Item).all()
            # Broadcast the received message to all connected clients
            for client in connected_clients:
                await client.send_text(json.dumps(data))
    except Exception as e:
        print(e)
        pass
    finally:
        # Remove the disconnected WebSocket from the list
        connected_clients.remove(websocket)


async def send_dummy_message():
    while True:
        await asyncio.sleep(1)  # Wait for 1 second
        message = {"message": "Dummy Message"}
        j = json.dumps(message)
        # print(len(connected_clients))
        for client in connected_clients:
            await client.send_text(j)
loop = asyncio.get_event_loop()

loop.create_task(send_dummy_message())
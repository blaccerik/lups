from fastapi import APIRouter, WebSocket, Depends, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from utils.database import get_db
from models.models import Item

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/api/websocket/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

router = APIRouter(prefix="/api/websocket")


@router.get("/")
async def get():
    return HTMLResponse(html)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            items = db.query(Item).all()
            await websocket.send_text(f"Message text was: {data} {items}")
    except WebSocketDisconnect:
        pass

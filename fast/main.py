from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from routers import items, websocket, chat
from utils.celery_config import celery_app
from utils.database import get_db

# Create an instance of FastAPI
app = FastAPI()

app.include_router(items.router)
app.include_router(websocket.router)
app.include_router(chat.router)


# Define a route (endpoint) and its response
@app.get("/")
async def read_root(db: Session = Depends(get_db)):
    return {"message": "Hello, World!"}


@app.get("/time")
async def time():
    task_name = "simple_task"
    task = celery_app.send_task(task_name)
    result = task.get()
    return result

from sqlalchemy.orm import Session

from database.models import DBSong
from utils.celery_config import celery_app


def start_scrape_for_song(song_id: str, postgres_client: Session):
    postgres_client.add(DBSong(id=song_id, status="scrapping"))
    postgres_client.commit()
    celery_app.send_task("find_new_songs", args=[song_id], queue="music:1")

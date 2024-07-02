import requests
from sqlalchemy.orm import Session

from database.models import DBSong
from utils.celery_config import celery_app


def _is_song_id_valid(song_id: str):
    print("API CALL")
    # hack by https://gist.github.com/tonY1883/a3b85925081688de569b779b4657439b
    url = f"https://img.youtube.com/vi/{song_id}/mqdefault.jpg"
    response = requests.head(url, allow_redirects=True, timeout=3)
    return response.status_code == 200


def start_scrape_for_song(song_id: str, postgres_client: Session):
    if _is_song_id_valid(song_id):
        postgres_client.add(DBSong(id=song_id, status="working"))
        postgres_client.commit()
        celery_app.send_task("find_new_songs", args=[song_id], queue="music:1")

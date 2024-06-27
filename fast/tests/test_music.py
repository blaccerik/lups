import unittest
from unittest.mock import patch

from starlette.testclient import TestClient

from create_db import create_test_db
from database.models import DBSong
from database.postgres_database import get_postgres_db
from main import app
from tests.testing_database import get_test_postgres_db, get_test_session

app.dependency_overrides[get_postgres_db] = get_test_postgres_db
client = TestClient(app)


class TestMusicAPI(unittest.TestCase):
    def setUp(self):
        create_test_db()

    @patch('utils.scrapping._is_song_id_valid', return_value=True)
    @patch('utils.celery_config.celery_app.send_task')
    def test_get_song(self, mock_send_task, mock_is_song_id_valid):
        song_id = "12345678901"
        response = client.get(f"/api/music/song/{song_id}")

        self.assertEqual(response.status_code, 404)
        mock_send_task.assert_called_once_with('find_new_songs', args=[song_id], queue="music:1")

        session = get_test_session()
        dbs = session.get(DBSong, song_id)
        self.assertEqual(dbs.id, song_id)
        self.assertEqual(dbs.status, "working")
        session.close()

        # some time passes
        session = get_test_session()
        dbs = session.get(DBSong, song_id)
        dbs.title = "test 1"
        dbs.status = "ready"
        dbs.length = 10
        dbs.artist_id = None
        dbs.type = "MUSIC_VIDEO_TYPE_UGC"
        session.add(dbs)
        session.commit()
        session.close()

        response = client.get(f"/api/music/song/{song_id}")

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["id"], song_id)
        self.assertEqual(data["title"], "test 1")
        self.assertEqual(data["length"], 10)

        mock_send_task.assert_called_once()



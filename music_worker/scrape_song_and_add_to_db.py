from database.postgres_database import SessionLocal
from task.music_task2 import find_new_songs_by_song_id

if __name__ == '__main__':
    postgres_client = SessionLocal()
    try:
        song_id = "ui_u0M7_hjs"
        find_new_songs_by_song_id(song_id, postgres_client)
    finally:
        postgres_client.close()
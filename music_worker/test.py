from database.postgres_database import SessionLocal
from task.music_task2 import download_by_song_id

if __name__ == '__main__':
    postgres_client = SessionLocal()

    song_id = "wpItKgAHVLY"
    new_artists, new_songs = download_by_song_id(song_id, postgres_client)
    print(new_artists, new_songs)
    # logger.info(f"a: {new_artists} | s: {new_songs}")

    postgres_client.close()

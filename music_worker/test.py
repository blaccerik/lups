from database.postgres_database import SessionLocal
from task.music_task2 import download_by_song_id, select_random_song

if __name__ == '__main__':
    postgres_client = SessionLocal()
    # song_id = "wpItKgAHVLY"
    # song_id = "Phu41Dx_01Q"
    # song_id = "jRqhGC5vgC0"
    for i in range(25):
        song_id = select_random_song(postgres_client)
        new_artists, new_songs, new_cons = download_by_song_id(song_id, postgres_client)
        print(new_artists, new_songs, new_cons)
    # logger.info(f"a: {new_artists} | s: {new_songs}")

    postgres_client.close()

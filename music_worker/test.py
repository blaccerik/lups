from database.postgres_database import SessionLocal
from task.music_task import get_song_watch_data, add_artists_to_db, add_songs_to_db, get_next_seed_song_id

if __name__ == '__main__':
    postgres_client = SessionLocal()

    for i in range(1):
        seed_song_id = get_next_seed_song_id(postgres_client)

        # seed_song_id = "cen0rBKLuYE"
        # seed_song_id = "L_w2Hu3Mhq4"
        # seed_song_id = "e7kJRGPgvRQ"
        # seed_song_id = "jtr2q0GRDGA"
        # seed_song_id = "ZCF9H66l0lE"
        # seed_song_id = "ttB80bhoU1s"
        # seed_song_id = "nGoOYNsM54I"
        # try:
        #     songs, artists, song_images, seed_song = get_song_watch_data(seed_song_id)
        #     add_artists_to_db(artists, postgres_client)
        #     add_songs_to_db(seed_song, songs, song_images, postgres_client)
        # except Exception as e:
        #     print(e)
        #     break

    postgres_client.close()

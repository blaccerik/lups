from database.postgres_database import SessionLocal

if __name__ == '__main__':
    postgres_client = SessionLocal()
    try:
        ta = 0
        ts = 0
        tc = 0

    # # song_id = "wpItKgAHVLY"
    # # # song_id = "Phu41Dx_01Q"
    # # # song_id = "jRqhGC5vgC0"
    # # new_artists, new_songs, new_connections = download_by_song_id(song_id, postgres_client)
    # # print(new_artists, new_songs, new_connections)
    # # print("-------")
    # for i in range(50):
    #     song_id = select_random_song(postgres_client)
    #     new_artists, new_songs, new_connections, new_connections2 = download_by_song_id(song_id, postgres_client)
    #     print(new_artists, new_songs, new_connections, new_connections2)
    finally:
        postgres_client.close()

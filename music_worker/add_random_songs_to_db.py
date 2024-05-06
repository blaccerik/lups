from database.postgres_database import SessionLocal
from task.music_task2 import download_by_song_id2
from util.downloadv2 import add_all

if __name__ == '__main__':
    postgres_client = SessionLocal()
    try:
        ta = 0
        ts = 0
        tc = 0
        for song_id in add_all():
            new_artists, new_songs, new_connections = download_by_song_id2(song_id, postgres_client)
            print(new_artists, new_songs, new_connections)
            ta += new_artists
            ts += new_songs
            tc += new_connections
        print("-----")
        print(ta, ts, tc)

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

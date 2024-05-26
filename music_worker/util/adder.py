from sqlalchemy.orm import Session

from database.models import DBArtist, DBSong, DBSongRelationV2
from schemas.main import Result


class Adder:
    def __init__(self, postgres_client: Session):
        self.song_images = {}
        self.artist_data = {}
        self.song_data = {}
        self.connection_data = {}

        self.postgres_client = postgres_client

    def add_to_db(self):
        # add new artists to db
        artist_ids = [i.id for i in self.postgres_client.query(DBArtist.id).filter(
            DBArtist.id.in_(self.artist_data)
        ).all()]
        new_artists = [self.artist_data[a] for a in self.artist_data if a not in artist_ids]
        self.postgres_client.add_all(new_artists)
        self.postgres_client.flush()

        # add new songs to db
        db_songs = {s.id: s for s in self.postgres_client.query(DBSong).filter(
            DBSong.id.in_(self.song_data)
        ).all()}
        new_songs = []
        for s in self.song_data:
            if s not in db_songs:
                new_songs.append(self.song_data[s])
            elif db_songs[s].status == "scrapping":
                dbs = db_songs[s]
                new_dbs = self.song_data[s]
                dbs.status = "ready"
                dbs.title = new_dbs.title
                dbs.length = new_dbs.length
                dbs.artist_id = new_dbs.artist_id
                dbs.type = new_dbs.type
                new_songs.append(dbs)
            else:
                del self.song_images[s]
        self.postgres_client.add_all(new_songs)
        self.postgres_client.flush()
        con_ids = [c.id for c in self.postgres_client.query(DBSongRelationV2.id).filter(
            DBSongRelationV2.id.in_(self.connection_data)
        ).all()]
        new_connections = []
        for c in self.connection_data:
            c_swap = c[11:] + c[:11]
            if not (c in con_ids or c_swap in con_ids):
                new_connections.append(self.connection_data[c])
        self.postgres_client.add_all(new_connections)
        self.postgres_client.commit()

    def add_artist(self, artist_id, artist_name):
        if artist_id is None or artist_id in self.artist_data:
            return
        dba = DBArtist(
            name=artist_name,
            id=artist_id
        )
        self.artist_data[artist_id] = dba

    def add_song(self, song_id, song_title, number, artist_id, song_type, image_link):
        if song_id in self.song_data:
            return
        dbs = DBSong(
            id=song_id,
            status="idle",
            title=song_title,
            length=number,
            artist_id=artist_id,
            type=song_type
        )
        self.song_data[song_id] = dbs
        self.song_images[song_id] = image_link

    def add_connection(self, seed_song_id, song_id):
        if seed_song_id == song_id:
            return
        key1 = seed_song_id + song_id
        key2 = song_id + seed_song_id
        if key1 in self.connection_data or key2 in self.connection_data:
            return
        dbsr = DBSongRelationV2(id=key1)
        self.connection_data[key1] = dbsr
        self.connection_data[key2] = dbsr

    def get_results(self) -> Result:
        return Result(artist_image_ids=[a.id for a in self.artist_data.values()], songs=self.song_images)

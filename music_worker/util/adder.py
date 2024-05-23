from sqlalchemy.orm import Session

from database.models import DBArtist, DBSong, DBSongRelationV2
from schemas.main import Result


class Adder:
    def __init__(self, postgres_client: Session):
        self.artists = {}
        self.song_images = {}
        self.songs = {}
        self.connections = {}
        self.postgres_client = postgres_client

    def add_to_db(self):
        self.postgres_client.add_all(self.artists.values())
        self.postgres_client.flush()
        self.postgres_client.add_all(self.songs.values())
        self.postgres_client.flush()
        self.postgres_client.add_all(self.connections.values())
        self.postgres_client.commit()

    def add_artist(self, artist_id, artist_name):
        if artist_id is None:
            return
        if artist_id in self.artists:
            return
        if self.postgres_client.get(DBArtist, artist_id):
            return
        dba = DBArtist(
            name=artist_name,
            id=artist_id
        )
        self.artists[artist_id] = dba

    def add_song(self, song_id, song_title, number, artist_id, song_type, image_link):
        if song_id in self.songs:
            return
        if self.postgres_client.get(DBSong, song_id):
            return
        dbs = DBSong(
            id=song_id,
            status="idle",
            title=song_title,
            length=number,
            artist_id=artist_id,
            type=song_type
        )
        self.songs[song_id] = dbs
        self.song_images[song_id] = image_link

    def add_connection(self, seed_song_id, song_id):
        if seed_song_id == song_id:
            return
        key1 = seed_song_id + song_id
        key2 = song_id + seed_song_id
        if key1 in self.connections:
            return
        if key2 in self.connections:
            return
        dbsr = self.postgres_client.get(DBSongRelationV2, key1)
        if dbsr:
            return
        dbsr = self.postgres_client.get(DBSongRelationV2, key2)
        if dbsr:
            return
        dbsr = DBSongRelationV2(
            id=key1
        )
        self.connections[key1] = dbsr

    def get_results(self) -> Result:
        artists = [a.id for a in self.artists.values()]
        return Result(artist_image_ids=artists, songs=self.song_images)

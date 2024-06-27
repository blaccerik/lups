import random
import time

from sqlalchemy import and_

from database.models import DBSong, DBSongRelationV1, DBArtist, DBUser, DBScrapeV1, DBReaction
from database.postgres_database import SessionLocal, Base, engine


def q(seed_id, user_id):
    r = postgres_client.query(DBSong, DBSongRelationV1).outerjoin(
        DBSongRelationV1, and_(
            DBSongRelationV1.child_song_id == DBSong.id,
            DBSongRelationV1.parent_song_id == seed_id
        )
    ).filter(DBSongRelationV1.id != None).outerjoin(
        DBReaction, and_(
            DBSong.id == DBReaction.song_id,
            DBReaction.user_id == user_id
        )
    ).filter(DBReaction.id == None)
    return [i[0].id for i in r]

def q2(seed_id, user_id):
    r = postgres_client.query(DBSong, DBSongRelationV1, DBScrapeV1).filter(
        DBSong.id == DBSongRelationV1.child_song_id,
        DBSongRelationV1.parent_song_id == seed_id
    ).outerjoin(
        DBReaction,
        and_(
            DBReaction.song_id == DBSongRelationV1.child_song_id,
            DBReaction.user_id == user_id
        )
    ).filter(DBReaction.id == None).outerjoin(
        DBScrapeV1,
        DBScrapeV1.id == DBSongRelationV1.child_song_id
    )
    return [i[0].id for i in r]


def q3(seed_id, user_id):
    r = postgres_client.query(DBSong, DBSongRelationV1).filter(and_(
        DBSong.id == DBSongRelationV1.child_song_id,
        DBSongRelationV1.parent_song_id == seed_id,
        ~DBSongRelationV1.child_song_id.in_(
            postgres_client.query(DBReaction.song_id).filter(
                DBReaction.user_id == user_id
            )
        )
    ))
    return [i[0].id for i in r]

if __name__ == '__main__':

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    postgres_client = SessionLocal()

    postgres_client.add(DBArtist(
        id="1",
        name="1"
    ))
    postgres_client.add(DBUser(
        id=1,
        google_id="1",
        name="1"
    ))
    postgres_client.add(DBUser(
        id=2,
        google_id="2",
        name="2"
    ))
    postgres_client.commit()

    song_nr = 100
    for i in range(song_nr):
        postgres_client.add(DBSong(
            id=f"s{i}",
            title=f"s{i}",
            length=1,
            artist_id=1,
            type="MUSIC_VIDEO_TYPE_UGC"
        ))
    postgres_client.commit()
    print(1)
    random.seed(1)
    for i in range(song_nr * 50):
        k1 = random.randint(0, song_nr - 1)
        k2 = random.randint(0, song_nr - 1)
        if k1 == k2:
            continue
        postgres_client.add(DBSongRelationV1(
            parent_song_id=f"s{k1}",
            child_song_id=f"s{k2}"
        ))
        postgres_client.add(DBSongRelationV1(
            parent_song_id=f"s{k2}",
            child_song_id=f"s{k1}"
        ))
        postgres_client.commit()
    print(2)
    for i in range(300):
        k1 = random.randint(0, song_nr - 1)
        if postgres_client.get(DBScrapeV1, f"s{k1}") is None:
            postgres_client.add(DBScrapeV1(
                id=f"s{k1}",
            ))
        postgres_client.commit()
    print(3)
    for i in range(song_nr * 2):
        k1 = random.randint(0, song_nr - 1)
        u = random.randint(1, 2)
        postgres_client.add(DBReaction(
            song_id=f"s{k1}",
            user_id=u,
            type='listened',
            duration=1
        ))
        postgres_client.commit()

    print("begin")
    total = [0,0,0,0]
    for s in range(song_nr):
        for u in range(1, 2):

            sid = f"s{s}"

            # fastest
            t5 = time.time()
            r3 = q2(sid, u)
            t6 = time.time()

            t3 = time.time()
            r2 = q(sid, u)
            t4 = time.time()

            t7 = time.time()
            r4 = q3(sid, u)
            t8 = time.time()

            t1 = time.time()

            srs = postgres_client.query(DBSongRelationV1).filter(
                DBSongRelationV1.parent_song_id == sid
            ).all()
            cons = []
            for sr in srs:
                song2 = postgres_client.get(DBSong, sr.child_song_id)

                reaction = postgres_client.query(DBReaction).filter(and_(
                    DBReaction.song_id == song2.id,
                    DBReaction.user_id == u
                )).first()
                if reaction is not None:
                    continue
                cons.append(song2.id)
            t2 = time.time()
            total[0] += t2 - t1
            total[1] += t4 - t3
            total[2] += t6 - t5
            total[3] += t8 - t7
            print(sid)
            if set(cons) != set(r2) or set(cons) != set(r3) or set(cons) != set(r4):
                raise Exception("not equal")

    print(f"{total[0] / song_nr:.3f} {total[1] / song_nr:.3f} {total[2] / song_nr:.3f} {total[3] / song_nr:.3f}")

    postgres_client.close()
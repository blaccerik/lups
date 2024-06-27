from sqlalchemy import and_

from database.models import DBSong, DBSongRelationV1, DBArtist, DBUser, DBScrapeV1, DBReaction
from database.postgres_database import SessionLocal, Base, engine


def add_to_db(postgres_client, e):
    if e.id is None or postgres_client.get(type(e), e.id) is None:
        postgres_client.add(e)
        postgres_client.commit()


def add1():
    postgres_client = SessionLocal()

    add_to_db(postgres_client, DBArtist(
        id="1",
        name="1"))

    add_to_db(postgres_client, DBSong(
        id="song1",
        title="1",
        length=1,
        artist_id=1,
        type="MUSIC_VIDEO_TYPE_UGC"
    ))
    add_to_db(postgres_client, DBSong(
        id="song2",
        title="1",
        length=1,
        artist_id=1,
        type="MUSIC_VIDEO_TYPE_UGC"
    ))
    add_to_db(postgres_client, DBSongRelationV1(
        parent_song_id="song1",
        child_song_id="song2",
    ))

    print(postgres_client.query(DBSongRelationV1).all())

    postgres_client.delete(postgres_client.get(DBSong, "song1"))
    postgres_client.commit()

    print(postgres_client.query(DBSongRelationV1).all())
    postgres_client.close()


def query1():
    postgres_client = SessionLocal()

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    if True:
        add_to_db(postgres_client, DBArtist(
            id="1",
            name="1"
        ))

        add_to_db(postgres_client, DBUser(
            id=1,
            google_id="1",
            name="1"
        ))

        add_to_db(postgres_client, DBUser(
            id=2,
            google_id="2",
            name="2"
        ))

        add_to_db(postgres_client, DBSong(
            id="s1",
            title="1",
            length=1,
            artist_id=1,
            type="MUSIC_VIDEO_TYPE_UGC"
        ))
        add_to_db(postgres_client, DBSong(
            id="s2",
            title="1",
            length=1,
            artist_id=1,
            type="MUSIC_VIDEO_TYPE_UGC"
        ))
        add_to_db(postgres_client, DBSong(
            id="s3",
            title="1",
            length=1,
            artist_id=1,
            type="MUSIC_VIDEO_TYPE_UGC"
        ))
        add_to_db(postgres_client, DBSong(
            id="s4",
            title="1",
            length=1,
            artist_id=1,
            type="MUSIC_VIDEO_TYPE_UGC"
        ))

        add_to_db(postgres_client, DBSongRelationV1(
            parent_song_id="s1",
            child_song_id="s2"
        ))
        add_to_db(postgres_client, DBSongRelationV1(
            parent_song_id="s2",
            child_song_id="s1"
        ))

        add_to_db(postgres_client, DBSongRelationV1(
            parent_song_id="s1",
            child_song_id="s3"
        ))
        add_to_db(postgres_client, DBSongRelationV1(
            parent_song_id="s3",
            child_song_id="s1"
        ))

        add_to_db(postgres_client, DBSongRelationV1(
            parent_song_id="s2",
            child_song_id="s4"
        ))
        add_to_db(postgres_client, DBSongRelationV1(
            parent_song_id="s4",
            child_song_id="s2"
        ))

        add_to_db(postgres_client, DBScrapeV1(
            id="s1",
        ))

        add_to_db(postgres_client, DBScrapeV1(
            id="s2",
        ))

    seed_id = "s3"
    # gets all songs related to seed song
    # and its scrape data
    r = postgres_client.query(DBSong, DBSongRelationV1, DBScrapeV1).outerjoin(
        DBSongRelationV1, and_(
            DBSongRelationV1.child_song_id == DBSong.id,
            DBSongRelationV1.parent_song_id == seed_id
        )
    ).filter(DBSongRelationV1.id != None).outerjoin(
        DBScrapeV1, DBScrapeV1.id == DBSong.id
    )

    # print(r)
    for i in r:
        print(i)
    postgres_client.close()


def query2():
    postgres_client = SessionLocal()

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    add_to_db(postgres_client, DBArtist(
        id="1",
        name="1"
    ))

    add_to_db(postgres_client, DBUser(
        id=1,
        google_id="1",
        name="1"
    ))

    add_to_db(postgres_client, DBUser(
        id=2,
        google_id="2",
        name="2"
    ))

    add_to_db(postgres_client, DBSong(
        id="s1",
        title="1",
        length=1,
        artist_id=1,
        type="MUSIC_VIDEO_TYPE_UGC"
    ))
    add_to_db(postgres_client, DBSong(
        id="s2",
        title="1",
        length=1,
        artist_id=1,
        type="MUSIC_VIDEO_TYPE_UGC"
    ))
    add_to_db(postgres_client, DBSong(
        id="s3",
        title="1",
        length=1,
        artist_id=1,
        type="MUSIC_VIDEO_TYPE_UGC"
    ))
    add_to_db(postgres_client, DBSong(
        id="s4",
        title="1",
        length=1,
        artist_id=1,
        type="MUSIC_VIDEO_TYPE_UGC"
    ))

    add_to_db(postgres_client, DBSong(
        id="s5",
        title="1",
        length=1,
        artist_id=1,
        type="MUSIC_VIDEO_TYPE_UGC"
    ))

    add_to_db(postgres_client, DBSong(
        id="s6",
        title="1",
        length=1,
        artist_id=1,
        type="MUSIC_VIDEO_TYPE_UGC"
    ))

    add_to_db(postgres_client, DBSongRelationV1(
        parent_song_id="s1",
        child_song_id="s2"
    ))
    add_to_db(postgres_client, DBSongRelationV1(
        parent_song_id="s2",
        child_song_id="s1"
    ))

    add_to_db(postgres_client, DBSongRelationV1(
        parent_song_id="s1",
        child_song_id="s3"
    ))
    add_to_db(postgres_client, DBSongRelationV1(
        parent_song_id="s3",
        child_song_id="s1"
    ))

    add_to_db(postgres_client, DBSongRelationV1(
        parent_song_id="s1",
        child_song_id="s4"
    ))
    add_to_db(postgres_client, DBSongRelationV1(
        parent_song_id="s4",
        child_song_id="s1"
    ))

    add_to_db(postgres_client, DBSongRelationV1(
        parent_song_id="s2",
        child_song_id="s5"
    ))
    add_to_db(postgres_client, DBSongRelationV1(
        parent_song_id="s5",
        child_song_id="s2"
    ))

    add_to_db(postgres_client, DBSongRelationV1(
        parent_song_id="s4",
        child_song_id="s6"
    ))
    add_to_db(postgres_client, DBSongRelationV1(
        parent_song_id="s6",
        child_song_id="s4"
    ))

    add_to_db(postgres_client, DBScrapeV1(
        id="s1",
    ))

    add_to_db(postgres_client, DBScrapeV1(
        id="s2",
    ))

    add_to_db(postgres_client, DBScrapeV1(
        id="s6",
    ))

    add_to_db(postgres_client, DBReaction(
        song_id="s1",
        user_id=1,
        type='listened',
        duration=1
    ))

    add_to_db(postgres_client, DBReaction(
        song_id="s4",
        user_id=1,
        type='listened',
        duration=1
    ))

    seed_id = "s1"
    user_id = 1
    # gets all songs related to seed song
    # and its scrape data
    r = postgres_client.query(DBSong, DBSongRelationV1, DBScrapeV1).outerjoin(
        DBSongRelationV1, and_(
            DBSongRelationV1.child_song_id == DBSong.id,
            DBSongRelationV1.parent_song_id == seed_id
        )
    ).filter(DBSongRelationV1.id != None).outerjoin(
        DBReaction, and_(
            DBSong.id == DBReaction.song_id,
            DBReaction.user_id == user_id
        )
    ).filter(DBReaction.id == None).outerjoin(
        DBScrapeV1, DBScrapeV1.id == DBSong.id
    )

    # print(r)
    for i in r:
        print(i)

    print("---------------------")

    r = postgres_client.query(DBSong, DBSongRelationV1).filter(
        DBSong.id == DBSongRelationV1.child_song_id,
        DBSongRelationV1.parent_song_id == seed_id
    ).outerjoin(
        DBReaction,
        and_(
            DBReaction.song_id == DBSongRelationV1.child_song_id,
            DBReaction.user_id == user_id
        )
    ).filter(DBReaction.id == None)
    for i in r:
        print(i)

    print("---------------------")
    r = postgres_client.query(DBSong, DBSongRelationV1).filter(and_(
        DBSong.id == DBSongRelationV1.child_song_id,
        DBSongRelationV1.parent_song_id == seed_id,
        ~DBSongRelationV1.child_song_id.in_(
            postgres_client.query(DBReaction.song_id).filter(
                DBReaction.user_id == user_id
            )
        )
    ))
    for i in r:
        print(i)
    postgres_client.close()


if __name__ == '__main__':
    query2()
    # postgres_client = SessionLocal()
    #
    # # for i in range(1000):
    # #     for j in range(1000):
    # #         postgres_client.add(DBSong(
    # #             id=f"{i}-{j}",
    # #             title="1",
    # #             length=2,
    # #             artist_id=1,
    # #             type="MUSIC_VIDEO_TYPE_UGC"
    # #         ))
    # #     postgres_client.commit()
    #
    # # postgres_client.add(DBSong(
    # #     id="6",
    # #     title="1",
    # #     length=1,
    # #     artist_id=1,
    # #     type="MUSIC_VIDEO_TYPE_UGC"
    # # ))
    # # postgres_client.commit()
    #
    # # postgres_client.add(DBReaction(
    # #     song_id="5",
    # #     user_id=2,
    # #     type="listened",
    # #     duration=1
    # # ))
    # # postgres_client.commit()
    #
    # # Reaction = aliased(DBReaction)
    #
    # # get all songs by user without reaction
    # t1 = time.time()
    # query = postgres_client.query(DBSong).outerjoin(
    #     DBReaction, and_(DBSong.id == DBReaction.song_id, DBReaction.user_id == 3)
    # ).filter(DBReaction.id == None).yield_per(64)
    # count = 0
    # for s in query:
    #     # print(s)
    #     count += 1
    # t2 = time.time()
    # print(count)
    # print(t2 - t1)
    # # print(s[0].id, s[1].id)
    # postgres_client.close()

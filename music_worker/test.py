import random
import time

from database.postgres_database import SessionLocal
from task.music_task2 import download_by_song_id



def main1():
    random.seed(11)

    # generate data
    db = {}
    amount = 100_000
    connections = 50
    for i in range(amount):
        for _ in range(connections):
            a = random.randint(0, amount - 1)
            if i in db:
                db[i].add(a)
            else:
                db[i] = {a}

            if a in db:
                db[a].add(i)
            else:
                db[a] = {i}

    print("start")
    t1 = time.time()
    attempt = 3000
    banned = set()
    for _ in range(attempt):
        ts = time.time()
        result, nr = query(banned, db)
        te = time.time()
        print(len(result), nr, te - ts)
    t2 = time.time()
    print("took", t2 - t1)
    return

def query(banned, db):
    # query data
    start = 0
    queue = [start]
    in_search = set()
    result = []
    nr = 0
    while len(queue):
        item = queue.pop(0)
        nr += 1
        cons = db[item]
        for c in cons:
            if c in in_search:
                continue
            queue.append(c)
            in_search.add(c)

            if c in banned:
                continue
            result.append(c)
            banned.add(c)
            if len(result) == 40:
                return result, nr
    return result, nr

if __name__ == '__main__':
    # postgres_client = SessionLocal()
    main1()
    # song_id = "wpItKgAHVLY"
    # song_id = "Phu41Dx_01Q"
    # song_id = "jRqhGC5vgC0"
    # new_artists, new_songs = download_by_song_id(song_id, postgres_client)
    # print(new_artists, new_songs)
    # # logger.info(f"a: {new_artists} | s: {new_songs}")

    # postgres_client.close()

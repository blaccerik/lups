import random
import time

from database.postgres_database import SessionLocal
from task.music_task2 import download_by_song_id



def main1():
    random.seed(69)

    # generate data
    db = {}
    amount = 3000
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
    # results:
    # 40 6360 0.36654186248779297
    # 40 6687 0.30622100830078125
    # 40 7041 0.3215463161468506
    # 40 7617 0.34729719161987305
    # 40 11045 0.5045084953308105
    # 0 100001 3.6011691093444824
    # 0 100001 3.6106362342834473
    # load data to memory and search it in there
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

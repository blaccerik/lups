from celery import Celery
from redis import Redis

url = 'redis://localhost:6379/0'
app = Celery('tasks', broker=url, backend=url)


@app.task(name="test")
def add(x, y):
    return x + y


r = Redis(host='localhost', port=6379, db=0)
print(r.get("erik"))
r.set("erik", "tere")
print(r.get("erik"))
r.close()
# ssh erik@134.209.198.189 -i C:\Users\erik\.ssh/id_rsa

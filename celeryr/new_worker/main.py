from celery import Celery

url = 'redis://10.0.0.2:6379/0'
app = Celery('tasks', broker=url, backend=url)


@app.task(name="test")
def add(x, y):
    return x + y

#ssh erik@134.209.198.189 -i C:\Users\erik\.ssh/id_rsa
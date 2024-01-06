from celery import Celery

url = "redis://localhost:6379/0"
app = Celery(
    'tasks',
    broker=url,
    backend=url
)

if __name__ == '__main__':
    result = app.send_task('test', (46545, 443434234))
    print(result)
    print(result.get())
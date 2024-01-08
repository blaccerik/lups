from celery import Celery

url = "redis://10.0.0.2:6379/0"
# url = "redis://134.209.198.189:6379/0"
app = Celery(
    'tasks',
    broker=url,
    backend=url
)

if __name__ == '__main__':
    result = app.send_task('test', (1,1))
    print(result)
    print(result.get())
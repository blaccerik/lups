from celery import Celery

url = 'redis://10.0.0.1:6379/0'
app = Celery(
    'tasks',
    broker=url,
    backend=url
)

if __name__ == '__main__':
    result = app.send_task('test', (46545, 443434234))
    print(result.get())
import time

import requests

if __name__ == '__main__':
    url = "http://localhost:8000/api/place/"
    for i in range(3):
        t1 = time.time()
        response = requests.get(url)
        print(len(response.text))
        t2 = time.time()
        print(t2 - t1)

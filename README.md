# DEV ENV

## Prerequisites

* Python 3.10+
* Node 18
* Docker

```console
~/lups/lups$ npm i
~/lups/fast$ pip install -r requirements.txt
```

## Frontend (www.lyps.ee)

```console
~/lups/lups$ npm i
~/lups/lups$ ng serve
```

if 'ng' command didnt work you can try

```console
~/lups/lups$ npm run ng serve

```

or install it globally

```console
~/lups/lups$ npm install -g @angular/cli
~/lups/lups$ ng serve
```

## Frontend (music.lyps.ee)

Only one frontend can run at the same time

```console
~/lups/music$ npm i
~/lups/music$ ng serve
```

## Backend (dev)

Start database and workers

```console
~/lups$ docker compose -f docker-compose.dev.yaml up -d --build
```

Create / Reset database

```console
~/lups/fast$ python create_db.py
```

Run app

```console
~/lups/fast$ uvicorn main:app --reload
```

## Backend (docker)

```console
~/lups$ docker compose -f docker-compose.backend.yaml up -d --build
```

to create tables

```console
~/lups$ docker exec -ti fastapi /bin/bash
/app# python create_db.py
```

# ADVANCED

## Run tests

```console
~/lups/fast$ python -m unittest discover -s ./tests
```

## Generate oauth for yt api (browser needed)

```console
~/lups/music_worker$ pip install -r requirements.txt
~/lups/music_worker$ ytmusicapi oauth
```
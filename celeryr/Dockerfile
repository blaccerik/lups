# pull official base image
FROM python:3.10.9-slim-buster

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# postgre stuff
RUN apt-get update && apt-get -y install libpq-dev gcc

# cmake for llama cpp
RUN apt-get -y install build-essential

# install dependencies
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

## copy model
#COPY t5-model t5-model

# copy cpp model
COPY cpp-model cpp-model

# copy beat
COPY beat.py beat.py

COPY worker/key.txt key.txt

# copy project
COPY worker worker
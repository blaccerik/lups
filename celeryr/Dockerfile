#FROM blaccerik/llama-test:v1

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

# download model
RUN huggingface-cli download TheBloke/TinyLlama-1.1B-1T-OpenOrca-GGUF tinyllama-1.1b-1t-openorca.Q8_0.gguf --local-dir cpp-model --local-dir-use-symlinks False

# copy beat
COPY beat.py beat.py

COPY worker/key.txt key.txt

# copy project
COPY worker worker
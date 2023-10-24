# pull official base image
FROM python:3.10.9-slim-buster

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# postgre stuff
RUN apt-get update && apt-get -y install libpq-dev gcc

# install dependencies
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy model
COPY t5-model t5-model

# copy project
COPY worker worker
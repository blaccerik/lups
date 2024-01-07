FROM python:3.11-alpine

# set work directory
WORKDIR /usr/src/app

# cmake for llama cpp
#RUN apt-get -y install build-essential
RUN apk --no-cache add build-base

# Install PostgreSQL development package
RUN apk --no-cache add postgresql-dev

# install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# download model
RUN huggingface-cli download TheBloke/TinyLlama-1.1B-1T-OpenOrca-GGUF tinyllama-1.1b-1t-openorca.Q8_0.gguf --local-dir cpp-model --local-dir-use-symlinks False

# copy project
COPY core core
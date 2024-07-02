FROM python:3.11.8-bookworm

# Set the working directory
WORKDIR /usr/src/app

# install
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
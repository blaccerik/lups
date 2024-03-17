FROM python:3.11.8-bookworm

# Set the working directory
WORKDIR /usr/src/app

# install
COPY requirements.txt .
RUN pip install -r requirements.txt

RUN huggingface-cli download TheBloke/TinyLlama-1.1B-1T-OpenOrca-GGUF tinyllama-1.1b-1t-openorca.Q8_0.gguf --local-dir cpp-model --local-dir-use-symlinks False

COPY . .

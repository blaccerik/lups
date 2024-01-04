# pull official base image
FROM blaccerik/llama-test:v1

# set work directory
#WORKDIR /usr/src/app
#
## set environment variables
#ENV PYTHONDONTWRITEBYTECODE 1
#ENV PYTHONUNBUFFERED 1
#
## postgre stuff
#RUN apt-get update && apt-get -y install libpq-dev gcc

# cmake for llama cpp
#RUN apt update && apt-get -y install build-essential


#RUN add-apt-repository -y ppa:ubuntu-toolchain-r/test &&  \
#    apt install -y gcc-11 g++-11 &&  \
#    update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-11 60 --slave /usr/bin/g++ g++ /usr/bin/g++-11
#RUN pip install --upgrade pip &&  \
#    pipinstall --upgrade setuptools wheel &&  \
#    apt-get install build-essential



#RUN apt-get update
#RUN apt install curl -y
#RUN apt install cmake -y
#RUN pip install testresources
#
## get add repo
#RUN apt-get install -y software-properties-common
#RUN apt-get update
#
#RUN apt-get update
#RUN apt-get install -y gnupg
#RUN gpg --keyserver keyserver.ubuntu.com --recv-keys 1E9377A2BA9EF27F
#RUN gpg --export --armor 1E9377A2BA9EF27F | apt-key add -
#
#RUN add-apt-repository -y ppa:ubuntu-toolchain-r/test &&  \
#    apt-get update &&  \
#    apt-get install -y gcc-11 g++-11
#RUN update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-11 60 --slave /usr/bin/g++ g++ /usr/bin/g++-11
#
#RUN pip install --upgrade pip
#RUN pip install --upgrade setuptools wheel
#RUN apt-get install build-essential

#RUN apt update && \
#    apt install -y software-properties-common && \
#    add-apt-repository ppa:ubuntu-toolchain-r/test && \
#    apt install -y gcc-11
##
#RUN gcc-11 --version

RUN pip install llama-cpp-python

## install dependencies
#COPY requirements.txt .
#RUN pip install -r requirements.txt
#
## download model
#RUN huggingface-cli download TheBloke/TinyLlama-1.1B-1T-OpenOrca-GGUF tinyllama-1.1b-1t-openorca.Q8_0.gguf --local-dir cpp-model --local-dir-use-symlinks False
#
## copy beat
#COPY beat.py beat.py
#
#COPY worker/key.txt key.txt
#
## copy project
#COPY worker worker
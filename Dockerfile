FROM python:3.8-buster as builder

MAINTAINER Takeshi Kishiyama <kishiyama.t@gmail.com>

# Setting & Copy
WORKDIR /opt/app
COPY requirements.lock /opt/app

# Env
RUN apt-get -y update && \
    apt-get -y upgrade && \
    apt-get install --no-install-recommends -yq ssh git curl apt-utils && \
    apt-get install -yq gcc g++

# Libraries
## HSMM
RUN git clone https://github.com/kishiyamat/hsmmlearn.git && \
    cd hsmmlearn && \
    pip install -r requirements.txt && \
    python setup.py develop
## Others
RUN pip install -r requirements.lock

# Experiment
# COPY hyparam /opt/app
RUN git clone -b feature/add-dockerfile https://github.com/kishiyamat/lsj-162-replication.git

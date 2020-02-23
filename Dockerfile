FROM arungupta/couchbase

FROM python:3.7.3

EXPOSE 8088
ADD . /int20h
WORKDIR /int20h

RUN pip3 install -r requirements.txt

FROM python:3.9-alpine
MAINTAINER Christophe Lambin <christophe.lambin@gmail.com>

EXPOSE 8080

RUN apk add curl
RUN addgroup -S -g 1000 abc && adduser -S --uid 1000 --ingroup abc abc

WORKDIR /app
COPY Pipfile Pipfile.lock ./

RUN pip install --upgrade pip && \
    pip install pipenv && \
    pipenv install --system --ignore-pipfile

COPY *.py ./
COPY vpnmon vpnmon/

USER abc
ENTRYPOINT ["/usr/local/bin/python3", "vpnmon.py"]
CMD []

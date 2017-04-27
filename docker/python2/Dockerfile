FROM smueller18/python:2-alpine

MAINTAINER smueller18

RUN apk add --no-cache \
        libressl2.5-libcrypto@edge \
        libressl2.5-libssl@edge \
        librdkafka@community \
        librdkafka-dev@community \
    && \
    # because of https://github.com/gliderlabs/docker-alpine/issues/205
    apk add --no-cache --virtual .build-deps-testing \
            --repository http://dl-cdn.alpinelinux.org/alpine/edge/main \
            python2-dev \
    && \
    apk add --no-cache --virtual .build-deps \
        git \
        gcc \
        musl-dev \
        linux-headers \
        g++ \
        postgresql-dev && \
    ## preperations for installations
    # numpy
    ln -s /usr/include/locale.h /usr/include/xlocale.h && \
    # psycopg2
    apk add --no-cache libpq && \
    \
    # install python modules
    pip install \
          cython \
          psycopg2 \
          numpy \
          flask mistune flask_socketio eventlet \
          beautifulsoup4 html5lib \
          pysolar \
          confluent-kafka confluent-kafka[avro] avro kafka-connector requests \
          pytz \
    && \
    apk del --no-cache .build-deps .build-deps-testing && \
    rm -rf /var/cache/apk/*

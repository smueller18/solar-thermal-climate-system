FROM smueller18/python:3-alpine

MAINTAINER smueller18

RUN apk upgrade --no-cache

RUN apk add --no-cache \
        libressl2.5-libcrypto \
        libressl2.5-libssl \
        librdkafka \
        librdkafka-dev \
    && \
    apk add --no-cache --virtual .build-deps \
        gcc \
        musl-dev \
        linux-headers \
        g++ \
        python3-dev \
        postgresql-dev \
        # for scipy
        build-base openblas-dev freetype-dev pkgconfig gfortran \
    && \
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
    && \
    pip install \
          flask mistune flask_socketio eventlet \
          beautifulsoup4 html5lib \
          pysolar \
          confluent-kafka confluent-kafka[avro] avro-python3 kafka_connector requests \
          pytz \
          pandas scipy sklearn tsfresh \
    && \
    apk del --no-cache .build-deps && \
    rm -rf /var/cache/apk/*

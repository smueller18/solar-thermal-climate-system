FROM smueller18/python:3-alpine

MAINTAINER smueller18

RUN apk add --no-cache \
        libressl2.4-libcrypto@edge \
        libressl2.4-libssl@edge \
        librdkafka@community \
        librdkafka-dev@community && \
    apk add --no-cache --virtual .build-deps \
        gcc \
        python3-dev \
        musl-dev \
        linux-headers \
        g++ \
        postgresql-dev && \
        curl \
        git \
    ## preperations for installations
    # numpy
    ln -s /usr/include/locale.h /usr/include/xlocale.h && \
    # psycopg2
    apk add --no-cache libpq && \
    \
    # install pykafka-tools
    # install python modules
    pip install \
          avro_python3 \
          cython \
          psycopg2 \
          numpy \
          flask mistune flask_socketio \
          beautifulsoup4 html5lib \
          schedule \
          pysolar \
    && \
    pip install git+https://github.com/smueller18/pykafka-tools.git@0.1.8#egg=pykafka-tools --process-dependency-links --allow-all-external \
    && \
    apk del .build-deps && \
    rm -rf /var/cache/apk/*

FROM smueller18/python:3-alpine

MAINTAINER smueller18

RUN apk add --no-cache \
          libressl2.4-libcrypto@edge \
          libressl2.4-libssl@edge \
          librdkafka@community

RUN apk add --no-cache --virtual .build-deps \
          gcc \
          python3-dev \
          musl-dev \
          linux-headers \
          g++ \
          postgresql-dev \
          curl \
          git \
          librdkafka-dev@community \
    ## preperations for installations
      # numpy
      && ln -s /usr/include/locale.h /usr/include/xlocale.h \
      # psycopg2
      && apk add --no-cache	libpq \
    \
    # install python modules
    && pip install \
            cython \
            psycopg2 \
            numpy \
            flask mistune flask_socketio \
            beautifulsoup4 html5lib \
            schedule \
            pysolar \
            confluent-kafka confluent-kafka[avro] \
    \
    # delete build dependencies
    && apk del .build-deps \
    \
    && rm -rf /var/cache/apk/*

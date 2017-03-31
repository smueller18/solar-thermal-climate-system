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
    \
    # install cython for performance reasions
    && pip install cython \
    # install pykafka
    && pip install pykafka \
    \
    # install scientific
    && ln -s /usr/include/locale.h /usr/include/xlocale.h \
    && pip install numpy \
    \
    # install avro
    && pip install avro_python3 \
    \
    # install psycopg2
    && apk add --no-cache	libpq \
    && pip install psycopg2 \
    \
    # install flask, socketio
    && pip install flask \
    && pip install mistune \
    && pip install flask_socketio \
    \
    # install beautifulsoup4
    && pip install beautifulsoup4 html5lib \
    \
    # install schedule (scheduled task running in Python)
    && pip install schedule \
    \
    # install pysolar
    && pip install pysolar \
    \
    # install pykafka-tools
    && pip install git+https://github.com/smueller18/pykafka-tools.git@0.1.8#egg=pykafka-tools --process-dependency-links --allow-all-external \
    \
    # delete build dependencies
    && apk del .build-deps \
    \
    #TODO is this command needed?
    && rm -rf /var/cache/apk/*

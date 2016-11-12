FROM smueller18/base:python3-alpine

MAINTAINER smueller18

RUN apk add --no-cache --virtual .build-deps \
          gcc \
          python3-dev \
          musl-dev \
          postgresql-dev \
          curl \
    \
    # install pykafka
    && apk add --no-cache --repository http://dl-cdn.alpinelinux.org/alpine/edge/main/ \
            libressl2.4-libcrypto \
   		      libressl2.4-libssl \
    && apk add --no-cache --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing/ \
            librdkafka \
    && apk add --no-cache --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing/ --virtual .librdkafka \
            librdkafka-dev \
    && pip install pykafka \
    \
    # install avro
    && pip install avro_python3 \
    \
    # install psycopg2
    && apk add --no-cache	libpq \
    && pip install psycopg2 \
    \
    # install flask
    && pip install flask \
    \
    # delete build dependencies
    && apk del .build-deps \
    && apk del .librdkafka \
    \
    #TODO is this command needed?
    && rm -rf /var/cache/apk/*

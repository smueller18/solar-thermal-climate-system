FROM smueller18/base:python3-alpine

MAINTAINER smueller18

RUN apk add --no-cache --virtual .build-deps \
          gcc \
          python3-dev \
          musl-dev \
          # for numpy
          linux-headers \
          g++ \
          # end for numpy
          postgresql-dev \
          curl \
          git \
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
    && pip install cython mistune \
    && pip install flask_socketio \
    \
    # install pykafka-tools
    && pip install git+https://github.com/smueller18/pykafka-tools.git@0.1.8#egg=pykafka-tools --process-dependency-links --allow-all-external \
    \
    # delete build dependencies
    && apk del .build-deps \
    && apk del .librdkafka \
    \
    #TODO is this command needed?
    && rm -rf /var/cache/apk/*

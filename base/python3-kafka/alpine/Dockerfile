FROM smueller18/base:python3-alpine

MAINTAINER smueller18

RUN apk add --no-cache --virtual .build-deps \
          gcc \
          python3-dev \
          musl-dev \
          curl \
    && apk add --no-cache --repository http://dl-cdn.alpinelinux.org/alpine/edge/main/ \
            libressl2.4-libcrypto \
   		      libressl2.4-libssl \
    && apk add --no-cache --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing/ \
            librdkafka \
    && apk add --no-cache --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing/ --virtual .build-deps-testing \
            librdkafka-dev \
    && pip install avro_python3 \
    && pip install pykafka \
    && apk del .build-deps \
    && apk del .build-deps-testing \
    && rm -rf /var/cache/apk/*

COPY kafka.avsc /opt/config/kafka.avsc

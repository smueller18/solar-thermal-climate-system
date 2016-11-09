FROM smueller18/base:python3-alpine

MAINTAINER smueller18

RUN apk add --virtual .build-deps \
          gcc \
          python3-dev \
          musl-dev \
          curl
    && apk add --no-cache \
          libressl2.4-libcrypto@edge \
    		  libressl2.4-libssl@edge \
          librdkafka@testing \
    # check of neccessary
          librdkafka-dev@testing \
    && pip install avro_python3 \
    && pip install pykafka \
    && apk del .build-deps

COPY kafka.avsc /opt/config/kafka.avsc

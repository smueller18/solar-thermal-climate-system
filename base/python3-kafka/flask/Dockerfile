FROM smueller18/python3-kafka:alpine

MAINTAINER smueller18

RUN apk add --no-cache --virtual .build-deps \
          gcc \
          python3-dev \
          musl-dev \
    && pip install flask \
    && apk del .build-deps

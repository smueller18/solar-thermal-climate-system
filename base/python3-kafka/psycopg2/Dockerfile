FROM smueller18/python3-kafka:alpine

MAINTAINER smueller18

RUN apk add --no-cache --virtual .build-deps \
          gcc \
          python3-dev \
          musl-dev \
          postgresql-dev \
    && apk add --no-cache	libpq \
    && pip install psycopg2 \
    && apk del .build-deps

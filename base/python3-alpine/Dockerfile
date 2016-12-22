FROM python:3.6-alpine

MAINTAINER smueller18

RUN apk add --no-cache --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing/ gosu

RUN mkdir -p /storage /opt

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

WORKDIR /home

ENTRYPOINT ["sh", "/usr/local/bin/entrypoint.sh"]

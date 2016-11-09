FROM python:3.6-alpine

MAINTAINER smueller18

# adopted from https://github.com/biggis-project/biggis-infrastructure/blob/master/biggis-docker/biggis-pipeline/biggis-base/alpine/Dockerfile

ADD repositories /etc/apk/
RUN apk add --no-cache gosu@testing && \
    mkdir /storage /opt

COPY entrypoint.sh /usr/local/bin/entrypoint.sh

WORKDIR /home

ENTRYPOINT ["sh", "/usr/local/bin/entrypoint.sh"]

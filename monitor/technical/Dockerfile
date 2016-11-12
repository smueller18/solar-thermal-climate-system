FROM smueller18/base:python3-alpine

MAINTAINER smueller18

RUN apk add --no-cache --virtual .build-deps \
          gcc \
          python3-dev \
          musl-dev \
          curl \
    \
    # install flask
    && pip install flask \
    \
    # delete build dependencies
    && apk del .build-deps

COPY src /opt/monitor-technical
COPY start.sh /start.sh

EXPOSE 5000

WORKDIR /opt/monitor-technical

CMD ["/start.sh"]

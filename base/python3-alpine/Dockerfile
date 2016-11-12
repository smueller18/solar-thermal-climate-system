FROM python:3.6-alpine

MAINTAINER smueller18

RUN apk add --no-cache --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing/ gosu

# copied from https://github.com/nginxinc/docker-nginx/blob/master/mainline/alpine/Dockerfile:
# Bring in gettext so we can get `envsubst`, then throw
# the rest away. To do this, we need to install `gettext`
# then move `envsubst` out of the way so `gettext` can
# be deleted completely, then move `envsubst` back.


RUN apk add --no-cache --virtual .build-deps gcc \
    && apk add --no-cache --virtual .gettext gettext \
  	&& mv /usr/bin/envsubst /tmp/ \
  	\
  	&& runDeps="$( \
  		scanelf --needed --nobanner /usr/sbin/nginx /usr/lib/nginx/modules/*.so /tmp/envsubst \
  			| awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
  			| sort -u \
  			| xargs -r apk info --installed \
  			| sort -u \
  	)" \
  	&& apk add --no-cache --virtual .nginx-rundeps $runDeps \
  	&& apk del .build-deps \
  	&& apk del .gettext \
  	&& mv /tmp/envsubst /usr/local/bin/

RUN mkdir /storage /opt

COPY entrypoint.sh /usr/local/bin/entrypoint.sh

WORKDIR /home

ENTRYPOINT ["sh", "/usr/local/bin/entrypoint.sh"]

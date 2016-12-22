FROM nginx:alpine

MAINTAINER smueller18

RUN apk add --no-cache --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing/ gosu

RUN mkdir -p /storage /opt

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

WORKDIR /etc/nginx

ENTRYPOINT ["sh", "/usr/local/bin/entrypoint.sh"]

CMD ["nginx", "-g", "daemon off;"]

#!/bin/sh

#exec cat /etc/nginx/http.template.conf
#exec echo $DOCKER_HOST_IP
#exec ls -lh /etc/nginx/
#exec echo --------------
#exec ls -lh /etc/nginx/htpasswd
#exec echo --------------
#exec ls -lh /etc/nginx/conf.d
#exec gosu root:root echo 0 > /etc/nginx/http.conf

#ls -lh /etc/nginx
#ls -lh /var/log/nginx
#ls -lh /dev

#USER=${USER_NAME:-user}
#chown $USER:$USER /etc/nginx

envsubst < /etc/nginx/http.template.conf > /etc/nginx/http.conf
#envsubst < /etc/nginx/http.template.conf > /etc/nginx/http.conf

#exec echo 1
exec nginx -g 'daemon off;'

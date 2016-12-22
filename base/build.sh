#!/bin/sh

docker build -t "smueller18/base:anaconda3" ./anaconda3
docker build -t "smueller18/base:python3-alpine" ./python3-alpine
docker build -t "smueller18/base:python3-kafka" ./python3-kafka

# do not build because it is not used
# docker build -t "smueller18/base:nginx" ./nginx

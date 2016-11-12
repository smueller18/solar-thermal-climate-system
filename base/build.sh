#!/bin/sh

docker build -t "smueller18/base:python3-alpine" ./python3-alpine
docker build -t "smueller18/base:python3-kafka" ./python3-kafka
docker build -t "smueller18/base:nginx" ./nginx

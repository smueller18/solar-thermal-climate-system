#!/bin/sh

docker build -t "smueller18/stcs:python2" ./python2
docker build -t "smueller18/stcs:python3" ./python3
docker build -t "smueller18/stcs:anaconda3" ./anaconda3
docker build -t "smueller18/stcs:python3-mqtt" ./python3-mqtt

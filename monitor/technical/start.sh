#!/bin/sh

envsubst < /home/monitor-technical/config.template.js > /opt/monitor-technical/static/js/config.js

exec python app.py

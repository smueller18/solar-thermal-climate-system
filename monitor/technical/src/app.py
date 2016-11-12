#!/usr/bin/env python3

# todo handle pykafka if logging Encountered SocketDisconnectedError while requesting metadata from broker
# destroy old consumer thread and start new one

import os
import datetime
import signal
import logging
import json
from flask import Flask

__author__ = "Stephan Müller"
__license__ = "MIT"

PORT = int(os.getenv("PORT", 5000))
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")
LOGGING_FORMAT = os.getenv("LOGGING_FORMAT", "%(levelname)8s %(asctime)s %(name)s [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s")


logging.basicConfig(format=LOGGING_FORMAT)
logger = logging.getLogger('app')
logger.setLevel(logging.getLevelName(LOGGING_LEVEL))


app = Flask(__name__)


@app.route('/')
def root():
    return app.send_static_file('index.html')


@app.route('/<path:path>')
def static_proxy(path):
    return app.send_static_file(path)


logger.info("Starting monitor-technical at port " + str(PORT))
app.run(host="0.0.0.0", port=PORT)

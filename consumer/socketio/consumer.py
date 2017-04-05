#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging.config
import threading
from flask import Flask, render_template, Markup
from flask_socketio import SocketIO, emit
import mistune
from kafka_connector.avro_loop_consumer import default_config
from kafka_connector.avro_loop_consumer import AvroLoopConsumer

__author__ = u'Stephan Müller'
__copyright__ = u'2017, Stephan Müller'
__license__ = u'MIT'

__dirname__ = os.path.dirname(os.path.abspath(__file__))

PORT = int(os.getenv("PORT", 5002))
KAFKA_HOSTS = os.getenv("KAFKA_HOSTS", "kafka:9092")
SCHEMA_REGISTRY_URL = os.getenv("SCHEMA_REGISTRY_URL", "http://schema-registry:8082")
CONSUMER_GROUP = os.getenv("CONSUMER_GROUP", "socketio")
TOPIC_PREFIX = os.getenv("TOPIC_PREFIX", "stcs.")
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")
logging_format = "%(levelname)8s %(asctime)s %(name)s [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"

logging.basicConfig(level=logging.getLevelName(LOGGING_LEVEL), format=logging_format)
logger = logging.getLogger('consumer')


cache = dict()


app = Flask(__name__, static_url_path='')
app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app, logger=True, engineio_logger=True, ping_timeout=10, ping_interval=5)

renderer = mistune.Renderer(escape=False, hard_wrap=True, use_xhtml=True)
markdown = mistune.Markdown(renderer=renderer)


# serve API description
@app.route('/')
def api_description():
    global markdown
    api_description_file = __dirname__ + "/API.md"
    content = markdown(open(api_description_file, "rb").read().decode())
    return render_template('index.html', content=Markup(content))


# SocketIO
counter_lock = threading.Lock()
connected_clients = 0


@socketio.on('connect')
def connect():
    global connected_clients
    counter_lock.acquire()
    connected_clients += 1
    counter_lock.release()
    socketio.emit('connected_clients', connected_clients, broadcast=True)
    for topic in cache:
        message = {'topic': topic}
        message.update(cache[topic])
        emit('sensor_values_cache', message)


@socketio.on('disconnect')
def disconnect():
    global connected_clients
    counter_lock.acquire()
    connected_clients -= 1
    # should never happen
    if connected_clients < 0:
        connected_clients = 0
    counter_lock.release()
    emit('connected_clients', connected_clients, broadcast=True)


def handle_message(msg):
    global socketio

    if len(msg.value()) > 0:

        if msg.topic() not in cache:
            cache[msg.topic()] = dict()

        cache[msg.topic()].update(msg.value())

        if type(msg.key()) is dict and "timestamp" in msg.key():
            message = {
                "timestamp": msg.key()["timestamp"],
                "data": msg.value(),
                "topic": msg.topic()
            }
            socketio.start_background_task(socketio.emit, 'sensor_values', message)
            logger.warning("sensor_values: " + str(message))


def run_kafka_consumer():

    # adjust config
    config = default_config

    # todo add start with latest

    consumer = AvroLoopConsumer(KAFKA_HOSTS, SCHEMA_REGISTRY_URL, CONSUMER_GROUP,
                                ["^" + TOPIC_PREFIX.replace(".", r'\.') + ".*"])
    consumer.loop(lambda msg: handle_message(msg))
    logger.info("Started consumer thread")


def run_socketio():
    logger.info("Starting socketio at port " + str(PORT))
    socketio.run(app=app, host="0.0.0.0", port=PORT)


if __name__ == '__main__':

    socketio_thread = threading.Thread(target=run_socketio)
    consumer_thread = threading.Thread(target=run_kafka_consumer)

    socketio_thread.start()
    consumer_thread.start()

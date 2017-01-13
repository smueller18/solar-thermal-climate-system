#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging.config
import threading
import re
import time
from pykafka import KafkaClient
from flask import Flask, render_template, Markup
from flask_socketio import SocketIO, emit
import mistune
from pykafka_tools.kafka_consumer import KafkaConsumer

__author__ = u'Stephan Müller'
__copyright__ = u'2017, Stephan Müller'
__license__ = u'MIT'

__dirname__ = os.path.dirname(os.path.abspath(__file__))

PORT = int(os.getenv("PORT", 5002))
KAFKA_HOSTS = os.getenv("KAFKA_HOSTS", "kafka:9092")
KAFKA_SCHEMA = os.getenv("KAFKA_SCHEMA", __dirname__ + "/kafka.timestamp-data.avsc")
CONSUMER_GROUP = os.getenv("CONSUMER_GROUP", "web-redirect")
ALLOWED_TOPICS_REGEX = os.getenv("ALLOWED_TOPIC_REGEX", ".*")
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")
logging_format = "%(levelname)8s %(asctime)s %(name)s [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"

logging.basicConfig(level=logging.getLevelName(LOGGING_LEVEL), format=logging_format)

logger = logging.getLogger('consumer_web_redirect')

cache = dict()


app = Flask(__name__, static_url_path='')
app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app, async_mode='threading', logger=True, engineio_logger=True, ping_timeout=10, ping_interval=5)

renderer = mistune.Renderer(escape=False, hard_wrap=True, use_xhtml=True)
markdown = mistune.Markdown(renderer=renderer)


@app.route('/')
def api_description():
    global markdown
    api_description_file = __dirname__ + "/API.md"
    content = markdown(open(api_description_file, "rb").read().decode())
    return render_template('index.html', content=Markup(content))


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


def new_sensor_values(sender, message):
    if 'data' in message and len(message['data']) > 0:
        cache[sender.get_topic()].update(message)
        message.update({'topic': sender.get_topic()})
        socketio.start_background_task(socketio.emit, 'sensor_values', message)


def kafka_consumers():
    global socketio

    started = False
    while not started:
        started_threads = dict()
        try:
            client = KafkaClient(hosts=KAFKA_HOSTS)

            for topic in client.topics:
                if re.search(ALLOWED_TOPICS_REGEX, topic.decode()) is not None:

                    cache[topic.decode()] = dict()

                    thread = KafkaConsumer(KAFKA_HOSTS, topic.decode(), CONSUMER_GROUP,
                                           kafka_message_schema_file=KAFKA_SCHEMA)
                    thread.new_message_event += new_sensor_values

                    thread.start()

                    started_threads.update({
                        topic.decode(): thread
                    })
                    logger.info("Started consumer thread for topic " + topic.decode())
            started = True

        except Exception as e:
            logger.exception(e)
            time.sleep(30)


def run():
    logger.info("Starting web-redirect at port " + str(PORT))
    socketio.run(app=app, host="0.0.0.0", port=PORT)


if __name__ == '__main__':

    webapp_thread = threading.Thread(target=run)
    consumer_thread = threading.Thread(target=kafka_consumers)

    webapp_thread.start()
    consumer_thread.start()

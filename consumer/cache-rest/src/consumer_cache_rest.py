#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging.config
import threading
import re
import json
import time
from pykafka import KafkaClient
from flask import Flask
from pykafka_tools.kafka_consumer import KafkaConsumer

__author__ = u'Stephan Müller'
__copyright__ = u'2017, Stephan Müller'
__license__ = u'MIT'

__dirname__ = os.path.dirname(os.path.abspath(__file__))

PORT = int(os.getenv("PORT", 5001))
KAFKA_HOSTS = os.getenv("KAFKA_HOSTS", "kafka:9092")
KAFKA_SCHEMA = os.getenv("KAFKA_SCHEMA", __dirname__ + "/kafka.timestamp-data.avsc")
CONSUMER_GROUP = os.getenv("CONSUMER_GROUP", "cache-rest")
ALLOWED_TOPICS_REGEX = os.getenv("ALLOWED_TOPIC_REGEX", ".*")
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")
logging_format = "%(levelname)8s %(asctime)s %(name)s [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"

logging.basicConfig(level=logging.getLevelName(LOGGING_LEVEL), format=logging_format)

logger = logging.getLogger('consumer_cache_rest')


consumer_sensor_values = dict()
latest_sensor_values_json = json.dumps({'timestamp': 0, 'data': {}})


def handle_sensor_update(sender, sensor_values):
    global latest_sensor_values_json
    consumer_sensor_values.update({sender.get_topic(): sensor_values})

    latest_sensor_values = {'timestamp': 0, 'data': dict()}
    for topic in consumer_sensor_values:
        if consumer_sensor_values[topic]['timestamp'] > latest_sensor_values['timestamp']:
            latest_sensor_values['timestamp'] = consumer_sensor_values[topic]['timestamp']
            latest_sensor_values['data'].update(consumer_sensor_values[topic]['data'])
    latest_sensor_values_json = json.dumps(latest_sensor_values)


def kafka_consumers():
    started = False
    while not started:
        started_threads = dict()
        try:
            client = KafkaClient(hosts=KAFKA_HOSTS)

            for topic in client.topics:
                if re.search(ALLOWED_TOPICS_REGEX, topic.decode()) is not None:
                    thread = KafkaConsumer(KAFKA_HOSTS, topic.decode(), CONSUMER_GROUP,
                                           kafka_message_schema_file=KAFKA_SCHEMA)
                    thread.new_message_event += handle_sensor_update
                    thread.start()

                    started_threads.update({
                        topic.decode(): thread
                    })
                    logger.info("Started consumer thread for topic " + topic.decode())
            started = True

        except Exception as e:
            logger.exception(e)
            time.sleep(30)


app = Flask(__name__)


@app.route('/')
def index():
    return latest_sensor_values_json


def run():
    logger.info("Starting cache-rest at port " + str(PORT))
    app.run(host="0.0.0.0", port=PORT)


if __name__ == '__main__':
    webapp_thread = threading.Thread(target=run)
    consumer_thread = threading.Thread(target=kafka_consumers)

    webapp_thread.start()
    consumer_thread.start()

    webapp_thread.join()

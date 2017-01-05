#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging.config
import threading
import avro.io
import json
import time
from pykafka import KafkaClient
from flask import Flask
from kafka_consumer import KafkaConsumer

__author__ = u'Stephan Müller'
__copyright__ = u'2016, Stephan Müller'
__license__ = u'MIT'

__dirname__ = os.path.dirname(os.path.abspath(__file__))

PORT = int(os.getenv("PORT", 5001))
KAFKA_HOSTS = os.getenv("KAFKA_HOSTS", "localhost:9092")
KAFKA_SCHEMA = os.getenv("KAFKA_SCHEMA", __dirname__ + "/kafka.timestamp-data.avsc")
CONSUMER_GROUP = os.getenv("CONSUMER_GROUP", "cache-rest")
AUTO_COMMIT_INTERVAL = int(os.getenv("AUTO_COMMIT_INTERVAL", 60000))
LOGGING_INI = os.getenv("LOGGING_INI", __dirname__ + "/logging.ini")
logging_format = "%(levelname)8s %(asctime)s %(name)s [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"

if os.path.isfile(LOGGING_INI):
    logging.config.fileConfig(LOGGING_INI)
else:
    logging.basicConfig(level=logging.INFO, format=logging_format)

logger = logging.getLogger('app')


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
            kafka_message_schema = avro.schema.Parse(open(KAFKA_SCHEMA, "rb").read().decode())
            client = KafkaClient(hosts=KAFKA_HOSTS)

            for topic in client.topics:
                thread = KafkaConsumer(KAFKA_HOSTS, topic.decode(), CONSUMER_GROUP, kafka_message_schema=kafka_message_schema)
                thread.sensor_values_update_event += handle_sensor_update
                thread.start()

                started_threads.update({
                    topic.decode(): thread
                })
                logger.info("Started consumer thread for topic " + topic.decode())
            started = True

        except Exception as e:
            logger.error(e)
            time.sleep(3)


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
    consumer_thread.join()

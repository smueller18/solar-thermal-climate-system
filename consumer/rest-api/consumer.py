#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
import threading
from flask import Flask, jsonify, render_template, Markup
import mistune
import kafka_connector.avro_loop_consumer as avro_loop_consumer
from kafka_connector.avro_loop_consumer import AvroLoopConsumer

__author__ = u'Stephan Müller'
__copyright__ = u'2017, Stephan Müller'
__license__ = u'MIT'

__dirname__ = os.path.dirname(os.path.abspath(__file__))

PORT = int(os.getenv("PORT", 5001))
KAFKA_HOSTS = os.getenv("KAFKA_HOSTS", "kafka:9092")
SCHEMA_REGISTRY_URL = os.getenv("SCHEMA_REGISTRY_URL", "http://schema-registry:8082")
CONSUMER_GROUP = os.getenv("CONSUMER_GROUP", "rest-api")
TOPIC_PREFIX = os.getenv("TOPIC_PREFIX", "prod.stcs.")
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")
logging_format = "%(levelname)8s %(asctime)s %(name)s [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"

logging.basicConfig(level=logging.getLevelName(LOGGING_LEVEL), format=logging_format)
logger = logging.getLogger('consumer')

cache = dict()


app = Flask(__name__, static_url_path='')

renderer = mistune.Renderer(escape=False, hard_wrap=True, use_xhtml=True)
markdown = mistune.Markdown(renderer=renderer)


@app.route('/')
def api_description():
    global markdown
    api_description_file = __dirname__ + "/API.md"
    content = markdown(open(api_description_file, "rb").read().decode())
    return render_template('index.html', content=Markup(content))


@app.route('/topics')
def route_topics():
    if len(cache) == 0:
        return jsonify({'error': 'no topic available'})

    topics = dict()
    for topic in cache:
        if 'timestamp' in cache[topic] and 'data' in cache[topic]:
            topics[topic] = cache[topic]

        else:
            topics[topic] = {'error': 'no cached messages available'}

    return jsonify(topics)


@app.route('/topics/<topic>')
def route_topic(topic):

    if topic not in cache:
        return jsonify({'error': 'topic not available'})

    if 'data' in cache[topic]:
        result = cache[topic]
        result.update({'topic': topic})
        return jsonify(result)

    return jsonify({'error': 'no cached message available'})


def run_rest_api():
    logger.info("Starting TestAPI at port " + str(PORT))
    app.run(host="0.0.0.0", port=PORT)


def handle_message(msg):
    global cache

    if len(msg.value()) > 0:

        if type(msg.key()) is dict and "timestamp" in msg.key():
            message = {
                "timestamp": msg.key()["timestamp"] / 1000,
                "data": msg.value()
            }

            cache[msg.topic()] = message


def run_kafka_consumer():
    global cache

    config = avro_loop_consumer.default_config
    config['enable.auto.commit'] = True
    config['default.topic.config'] = dict()
    config['default.topic.config']['auto.offset.reset'] = 'latest'

    consumer = AvroLoopConsumer(KAFKA_HOSTS, SCHEMA_REGISTRY_URL, CONSUMER_GROUP,
                                ["^" + TOPIC_PREFIX.replace(".", r'\.') + ".*"])
    logger.info("Starting consumer thread...")

    try:
        consumer.loop(lambda msg: handle_message(msg))
    except Exception as e:
        logger.exception(e)
        consumer.close()

        return


if __name__ == '__main__':

    rest_api_thread = threading.Thread(name="RestAPI", target=run_rest_api)
    consumer_thread = threading.Thread(name="KafkaConsumer", target=run_kafka_consumer)

    rest_api_thread.start()
    consumer_thread.start()

    consumer_thread.join()
    rest_api_thread.join()

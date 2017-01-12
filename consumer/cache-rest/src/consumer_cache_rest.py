#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging.config
import threading
import re
import time
from pykafka import KafkaClient
from flask import Flask, jsonify, render_template, Markup
import mistune
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

topic_cache = dict()


def handle_sensor_update(sender, sensor_values):
    global topic_cache
    topic_cache[sender.get_topic()].update(sensor_values)


def kafka_consumers():
    started = False
    while not started:
        started_threads = dict()
        try:
            client = KafkaClient(hosts=KAFKA_HOSTS)

            for topic in client.topics:
                if re.search(ALLOWED_TOPICS_REGEX, topic.decode()) is not None:
                    topic_cache[topic.decode()] = dict()

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
    if len(topic_cache) == 0:
        return jsonify({'error': 'no topic available'})

    topics = dict()
    for topic in topic_cache:
        if 'timestamp' in topic_cache[topic] and 'data' in topic_cache[topic]:
            topics[topic] = topic_cache[topic]

    if len(topics) > 0:
        return jsonify(topics)

    return jsonify({'error': 'no cached messages available'})


@app.route('/topic/<topic>')
def route_topic(topic):

    if topic not in topic_cache:
        return jsonify({'error': 'topic not available'})

    if 'data' in topic_cache[topic]:
        result = topic_cache[topic]
        result.update({'topic': topic})
        return jsonify(result)

    return jsonify({'error': 'no cached message available'})


def run():
    logger.info("Starting cache-rest at port " + str(PORT))
    app.run(host="0.0.0.0", port=PORT)


if __name__ == '__main__':
    webapp_thread = threading.Thread(target=run)
    consumer_thread = threading.Thread(target=kafka_consumers)

    webapp_thread.start()
    consumer_thread.start()

    webapp_thread.join()

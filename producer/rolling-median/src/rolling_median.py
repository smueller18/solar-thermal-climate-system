#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import time
import numpy as np
import math
import logging.config
from pykafka import KafkaClient
from pykafka_tools.kafka_consumer import KafkaConsumer
from pykafka_tools.kafka_producer_pool import KafkaProducerPool

__author__ = u'Stephan Müller'
__copyright__ = u'2017, Stephan Müller'
__license__ = u'MIT'

__dirname__ = os.path.dirname(os.path.abspath(__file__))

KAFKA_HOSTS_CONSUMER = os.getenv("KAFKA_HOSTS_CONSUMER", "kafka:9092")
KAFKA_HOSTS_PRODUCER = os.getenv("KAFKA_HOSTS_PRODUCER", "kafka:9092")
KAFKA_SCHEMA = os.getenv("KAFKA_SCHEMA", "/avro/schema/kafka.timestamp-data.avsc")
CONSUMER_GROUP = os.getenv("CONSUMER_GROUP", "rolling-median")
ROLLING_MEDIAN_WINDOW = int(os.getenv("ROLLING_MEDIAN_WINDOW", 5))
ALLOWED_TOPICS_REGEX_CONSUMER = os.getenv("ALLOWED_TOPICS_REGEX_CONSUMER", ".*")
TOPIC_SUFFIX_PRODUCER = os.getenv("TOPIC_SUFFIX_PRODUCER", "_rolling_median")
LOGGING_INI = os.getenv("LOGGING_INI", __dirname__ + "/logging.ini")
logging_format = "%(levelname)8s %(asctime)s %(name)s [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"

if os.path.isfile(LOGGING_INI):
    logging.config.fileConfig(LOGGING_INI)
else:
    logging.basicConfig(level=logging.INFO, format=logging_format)

logger = logging.getLogger('rolling-median')

topics = dict()
kafka_producer_pool = None


def handle_sensor_update(sender, message):

    topics[sender.get_topic()].append(message)

    if len(topics[sender.get_topic()]) > ROLLING_MEDIAN_WINDOW:
        topics[sender.get_topic()].pop(0)

        timestamp = topics[sender.get_topic()][math.floor(ROLLING_MEDIAN_WINDOW / 2)]["timestamp"]
        produce_message = {"timestamp": timestamp, "data": dict()}

        for sensor_id in topics[sender.get_topic()][0]["data"]:
            values = list()
            for i in range(0, ROLLING_MEDIAN_WINDOW):
                values.append(topics[sender.get_topic()][i]["data"][sensor_id])
            produce_message["data"][sensor_id] = np.median(values)

        kafka_producer_pool.produce(sender.get_topic() + TOPIC_SUFFIX_PRODUCER, produce_message)


started = False
while not started:
    started_threads = dict()
    try:
        client = KafkaClient(hosts=KAFKA_HOSTS_CONSUMER)

        # read topics
        for topic in client.topics:
            if re.search(ALLOWED_TOPICS_REGEX_CONSUMER, topic.decode()) is not None:
                topics.update({topic.decode(): list()})

        # create producers
        topic_list = list()
        for topic in topics:
            topic_list.append(topic + TOPIC_SUFFIX_PRODUCER)
        kafka_producer_pool = KafkaProducerPool(KAFKA_HOSTS_PRODUCER, topic_list, KAFKA_SCHEMA)

        # create consumers
        for topic in topics:
            thread = KafkaConsumer(KAFKA_HOSTS_CONSUMER, topic, CONSUMER_GROUP, KAFKA_SCHEMA)
            thread.new_message_event += handle_sensor_update
            thread.start()
            logger.info("Started consumer thread for topic " + topic)

            started_threads.update({
                topic: thread
            })

        started = True

    except Exception as e:
        logger.exception(e)
        time.sleep(3)

while True:
    time.sleep(100)

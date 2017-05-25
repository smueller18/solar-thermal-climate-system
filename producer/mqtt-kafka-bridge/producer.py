#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
import datetime

from kafka_connector.avro_loop_producer import AvroLoopProducer

__author__ = u'Stephan Müller'
__copyright__ = u'2017, Stephan Müller'
__license__ = u'MIT'

__dirname__ = os.path.dirname(os.path.abspath(__file__))

KAFKA_HOSTS = os.getenv("KAFKA_HOSTS", "kafka:9092")
SCHEMA_REGISTRY_URL = os.getenv("SCHEMA_REGISTRY_URL", "http://schema-registry:8082")
MQTT_HOST = os.getenv("MQTT_HOST", "mosquitto:1883")
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "mqtt/topic")
PRODUCER_TOPIC = os.getenv("PRODUCER_TOPIC", "prod.stcs.???")

LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")
logging_format = "%(levelname)8s %(asctime)s %(name)s [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"

# TODO schema for every topic
key_schema = __dirname__ + "/config/key.avsc"
value_schema = __dirname__ + "/config/value.avsc"

logging.basicConfig(level=logging.getLevelName(LOGGING_LEVEL), format=logging_format)
logger = logging.getLogger('producer')


producer = AvroLoopProducer(KAFKA_HOSTS, SCHEMA_REGISTRY_URL, PRODUCER_TOPIC, key_schema, value_schema)

# TODO listening to mosquitto and producing to Kafka
while True:

    key = {'timestamp': int(time.time() * 1000)}
    value = {'value': 1}

    producer.produce(key, value)

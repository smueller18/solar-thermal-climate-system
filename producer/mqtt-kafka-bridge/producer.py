#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
import datetime
from glob import glob

import paho.mqtt.client as mqtt

from kafka_connector.avro_loop_producer import AvroLoopProducer

__author__ = u'Stephan Müller, Adrian Bürger'
__copyright__ = u'2017, Stephan Müller, Adrian Bürger'
__license__ = u'MIT'

__dirname__ = os.path.dirname(os.path.abspath(__file__))

KAFKA_HOSTS = os.getenv("KAFKA_HOSTS", "kafka:9092")
SCHEMA_REGISTRY_URL = os.getenv("SCHEMA_REGISTRY_URL", "http://schema-registry:8082")
MQTT_HOST = os.getenv("MQTT_HOST", "mosquitto:1883")

# MQTT_TOPIC = os.getenv("MQTT_TOPIC", "mqtt/topic")


# Collecto the name of all folders within the "config" directory, which
# corresponds to the names of all topics that we want to bridge Collect all the topics we want to bridge, and initialize according producers

mqtt_topics = glob("*")

producers = {}

for topic in mqtt_topics:

    PRODUCER_TOPIC = os.getenv("PRODUCER_TOPIC", "prod.stcs." + (topic))

    LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")
    logging_format = "%(levelname)8s %(asctime)s %(name)s [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"

    # TODO schema for every topic
    key_schema = os.path.join([__dirname__, "config", topic, "key.avsc"])
    value_schema = os.path.join([__dirname__, "config", topic, "value.avsc"])

    logging.basicConfig(level=logging.getLevelName(LOGGING_LEVEL), format=logging_format)
    logger = logging.getLogger('mqtt_kafka_bridge_topic_' + topic)

    producer = AvroLoopProducer(KAFKA_HOSTS, SCHEMA_REGISTRY_URL, PRODUCER_TOPIC, key_schema, value_schema)

    producers[topic] = producer


def on_connect(client, userdata, flags, rc):

    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("prod\stcs\+")


def on_message(client, userdata, msg):

    # her comes the publishing

    print(msg.topic+" "+str(msg.payload))



mqtt_client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

client.loop_forever()

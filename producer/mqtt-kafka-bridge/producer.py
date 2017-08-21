#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
import json

import paho.mqtt.client as mqtt

from kafka_connector.avro_loop_producer import AvroLoopProducer


__author__ = u'Stephan Müller, Adrian Bürger'
__copyright__ = u'2017, Stephan Müller, Adrian Bürger'
__license__ = u'MIT'

__dirname__ = os.path.dirname(os.path.abspath(__file__))

KAFKA_HOSTS = os.getenv("KAFKA_HOSTS", "kafka:9092")
SCHEMA_REGISTRY_URL = os.getenv("SCHEMA_REGISTRY_URL", "http://schema-registry:8082")

KAFKA_TOPICS_PREFIX = "dev.stcs."
MQTT_TOPICS_PREFIX = "prod/stcs/"

MQTT_SERVER_ADDRESS = os.getenv("MQTT_SERVER_ADDRESS", "mosquitto")
MQTT_SERVER_PORT = int(os.getenv("MQTT_SERVER_PORT", "1883"))

MQTT_QUALITY_OF_SERVICE = 0

MQTT_KEEPALIVE_TIME = 60

LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")
logging_format = "%(levelname)8s %(asctime)s %(name)s [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"

logging.basicConfig(level=logging.getLevelName(LOGGING_LEVEL), format=logging_format)
logger = logging.getLogger('mqtt_kafka_bridge')


# Collect the name of all folders within the "config" directory, which
# corresponds to the names of all topics that we want to bridge Collect 
# all the topics we want to bridge, and initialize according producers

kafka_subtopics = os.listdir(os.path.join(__dirname__, "config"))

mqtt_kafka_bridge = {}

mqtt_subscription_topics = []


for kafka_subtopic in kafka_subtopics:

    kafka_producer_topic = KAFKA_TOPICS_PREFIX + kafka_subtopic

    mqtt_topic = MQTT_TOPICS_PREFIX + kafka_subtopic.replace(".", "/")

    key_schema = os.path.join(__dirname__, "config", kafka_subtopic, "key.avsc")
    value_schema = os.path.join(__dirname__, "config", kafka_subtopic, "value.avsc")

    value_schema_file = open(value_schema, "r")
    value_schema_entries = [value_schema_entry["name"] for value_schema_entry \
        in json.load(value_schema_file)["fields"]]

    kafka_producer = AvroLoopProducer(KAFKA_HOSTS, SCHEMA_REGISTRY_URL, \
        kafka_producer_topic, key_schema, value_schema)

    mqtt_kafka_bridge[mqtt_topic] = {
        
        "kafka_producer": kafka_producer, 
        "value_schema_entries" : value_schema_entries
        
        }


def on_connect(client, userdata, flags, rc):

    logger.info("Connected to MQTT server with result code " + str(rc))

    mqtt_subscription_topics = [(mqtt_topic, MQTT_QUALITY_OF_SERVICE) for mqtt_topic \
        in mqtt_kafka_bridge.keys()]

    client.subscribe(mqtt_subscription_topics)
    
    logger.info("Subscribed to topics " + str(mqtt_subscription_topics))


def convert_mqtt_message_to_kafka_data(msg):

    kafka_data = {"key": None, "value": {}}

    try:

        mqtt_message_data = msg.payload.split(b";")

        kafka_data["key"] = {"timestamp": int(mqtt_message_data[0]) * 1000}

        for k, value_schema_entry in enumerate(mqtt_kafka_bridge[msg.topic]["value_schema_entries"]):

            kafka_data["value"][value_schema_entry] = int(mqtt_message_data[k+1]) / 100.0

        return kafka_data

    except:

        logger.error("Parsing the following MQTT message failed: " + str(msg.payload))

        return None


def publish_data_to_kafka(data, msg):

    if data:

        mqtt_kafka_bridge[msg.topic]["kafka_producer"].produce( \
            key = data["key"], value = data["value"])


def on_message(client, userdata, msg):

    logger.info("Received message on topic " + msg.topic)

    kafka_data = convert_mqtt_message_to_kafka_data(msg)

    publish_data_to_kafka(kafka_data, msg)


mqtt_client = mqtt.Client()

mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.connect(MQTT_SERVER_ADDRESS, MQTT_SERVER_PORT, MQTT_KEEPALIVE_TIME)

mqtt_client.loop_forever()

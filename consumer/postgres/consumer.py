#!/usr/bin/env python3

import os
import logging.config
import time

import psycopg2
from confluent_kafka.avro import CachedSchemaRegistryClient
import kafka_connector.avro_loop_consumer as avro_loop_consumer
from kafka_connector.avro_loop_consumer import AvroLoopConsumer
import postgres

__author__ = u'Stephan Müller'
__copyright__ = u'2017, Stephan Müller'
__license__ = u'MIT'

__dirname__ = os.path.dirname(os.path.abspath(__file__))


POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))
POSTGRES_DB = os.getenv("POSTGRES_DB", "postgres")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PW = os.getenv("POSTGRES_PW", "postgres")
KAFKA_HOSTS = os.getenv("KAFKA_HOSTS", "kafka:9092")
SCHEMA_REGISTRY_URL = os.getenv("SCHEMA_REGISTRY_URL", "http://schema_registry:8082")
CONSUMER_GROUP = os.getenv("CONSUMER_GROUP", "postgres")
TOPIC_PREFIX = os.getenv("TOPIC_PREFIX", "prod.")
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")
logging_format = "%(levelname)8s %(asctime)s %(name)s [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"

logging.basicConfig(level=logging.getLevelName(LOGGING_LEVEL), format=logging_format)

logger = logging.getLogger('consumer')


schema_registry = CachedSchemaRegistryClient(url=SCHEMA_REGISTRY_URL)

postgres_connector = postgres.Connector(host=POSTGRES_HOST, port=POSTGRES_PORT, database=POSTGRES_DB,
                                        user=POSTGRES_USER, password=POSTGRES_PW)

topics = dict()


def handle_message(msg):
    global postgres_connector

    topic = msg.topic().str()

    if topic not in topics:
        topics[topic] = {
            "table_name": topic.replace(TOPIC_PREFIX, "", 1),
            "table_check": False
        }

    try:
        if not topics[topic]["table_check"]:
            try:
                if not postgres_connector.table_exists(topic):
                    postgres_connector.create_table(table_name=topic, data=msg.value())
                    topics[topic]["table_check"] = True
                    logger.info("Created table for topic '" + topic + "'")
                else:
                    number_of_added_columns = postgres_connector.update_columns(table_name=topic, data=msg.value())
                    topics[topic]["table_check"] = True
                    logger.info("Added " + str(number_of_added_columns) + " columns in table for topic '" + topic + "'")

            except psycopg2.OperationalError:
                raise ConnectionError("Postgres operational error.")

        if topics[topic]["message_schema_check"]:
            postgres_connector.insert_values(table_name=topic, data=msg.value())
            # todo commit after successful db write
            #consumer.commit(msg, async=True)

    except Exception as e:
        logger.exception(e)
        exit(1)

"""
'default.topic.config': {
     'auto.offset.reset': 'earliest'
}
"""

config = avro_loop_consumer.default_config
config['enable.auto.commit'] = False
config['default.topic.config'] = dict()
config['default.topic.config']['auto.offset.reset'] = 'latest'


topic_regex = '^' + TOPIC_PREFIX.replace('.', r'\.') + '.*'
consumer = AvroLoopConsumer(KAFKA_HOSTS, SCHEMA_REGISTRY_URL, CONSUMER_GROUP, [topic_regex], config=config)
consumer.loop(lambda msg: handle_message(msg))

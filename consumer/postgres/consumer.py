#!/usr/bin/env python3

import os
import logging.config

import psycopg2
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
SCHEMA_REGISTRY_URL = os.getenv("SCHEMA_REGISTRY_URL", "http://schema-registry:8082")
CONSUMER_GROUP = os.getenv("CONSUMER_GROUP", "postgres")
TOPIC_PREFIX = os.getenv("TOPIC_PREFIX", "prod.")
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")
logging_format = "%(levelname)8s %(asctime)s %(name)s [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"

logging.basicConfig(level=logging.getLevelName(LOGGING_LEVEL), format=logging_format)

logger = logging.getLogger('consumer')


postgres_connector = postgres.Connector(host=POSTGRES_HOST, port=POSTGRES_PORT, database=POSTGRES_DB,
                                        user=POSTGRES_USER, password=POSTGRES_PW)

topics = dict()


def handle_message(msg):
    global postgres_connector

    if msg.key() is None or type(msg.key()) is not dict:
        logger.warning("Key is none. Ignoring message.")
        return
    elif msg.value() is None or type(msg.value()) is not dict:
        logger.warning("Value is none. Ignoring message.")
        return

    topic = msg.topic()

    topic_split = topic.split(".", 2)

    if len(topic_split) < 3:
        logging.warning("Table name cannot be derived from topic %s. Topic name must have at least 3 parts seperated "
                        "with dots. Ignoring message." % topic)
        return

    if topic not in topics:
        topics[topic] = {
            "table": topic_split[1] + ".public." + topic_split[2].replace(".", "__"),
            "table_check": False
        }

    try:
        if not topics[topic]["table_check"]:
            try:
                if not postgres_connector.table_exists(topics[topic]["table"]):
                    postgres_connector.create_table(table_name=topics[topic]["table"],
                                                    keys=msg.key(), values=msg.value())
                    topics[topic]["table_check"] = True
                    logger.info("Created table for topic '" + topic + "'")

            except psycopg2.OperationalError:
                raise ConnectionError("Postgres operational error.")

        if topics[topic]["table_check"]:

            try:
                postgres_connector.insert_values(table_name=topics[topic]["table"], data={**msg.key(), **msg.value()})

            except psycopg2.OperationalError as e:
                logger.exception(e)
                consumer.stop()
                return

            except psycopg2.DatabaseError:
                logger.error("Message with topic '%s' and offset % s was not inserted into database."
                             % (topic, msg.offset()))

            logging.info("Message with topic '%s' and offset %s was inserted into database."
                         % (topic, msg.offset()))

            consumer.commit(msg, async=True)

    except Exception as e:
        logger.exception(e)
        consumer.stop()


config = avro_loop_consumer.default_config
config['enable.auto.commit'] = False
config['default.topic.config'] = dict()
config['default.topic.config']['auto.offset.reset'] = 'largest'


topic_regex = '^' + TOPIC_PREFIX.replace('.', r'\.') + '.*'
consumer = AvroLoopConsumer(KAFKA_HOSTS, SCHEMA_REGISTRY_URL, CONSUMER_GROUP, [topic_regex], config=config)
consumer.loop(lambda msg: handle_message(msg))

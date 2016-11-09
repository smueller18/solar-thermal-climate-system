#!/usr/bin/env python3

import argparse
import datetime
import io
import json
import logging
import os
import threading

import avro.io
import psycopg2
from pykafka import KafkaClient

from connector import PostgresConnector

__author__ = "Stephan Müller"
__license__ = "MIT"


# todo add description
parser = argparse.ArgumentParser(description='')

parser.add_argument('-c', type=str, default="../config/config.json", help="config file")

args = parser.parse_args()
config_file = args.c

config = json.loads(open(config_file, "rb").read().decode())

logging.basicConfig(format=config["logging"]["format"])
logger = logging.getLogger('database_writer')
logger.setLevel(logging.getLevelName(config["logging"]["level"]))


kafka_message_schema_file = config["kafka"]["message_schema_file"]
if not os.path.isabs(kafka_message_schema_file):
    kafka_message_schema_file = os.path.dirname(os.path.abspath(config_file)) + "/" + kafka_message_schema_file
kafka_message_schema = avro.schema.Parse(open(kafka_message_schema_file, "rb").read().decode())

try:
    postgress_connector = PostgresConnector(host=config["database"]["host"],
                                            port=config["database"]["port"],
                                            database=config["database"]["name"],
                                            user=config["kafka-sink-postgres"]["database"]["user"],
                                            password=config["kafka-sink-postgres"]["database"]["password"])
except Exception as e:
    logger.error("Could not establish database connection: " + str(e))
    exit(1)


def decode_message(message):
    bytes_reader = io.BytesIO(message.value)
    decoder = avro.io.BinaryDecoder(bytes_reader)
    reader = avro.io.DatumReader(kafka_message_schema)
    return reader.read(decoder)


def loop_inserter(consumer):
    topic = consumer.topic.name.decode()
    # create or update table schema if necessary
    logger.debug("Waiting for first message of topic '" + topic + "'...")

    parsed_first_message_correctly = False
    while not parsed_first_message_correctly:
        try:
            first_message = decode_message(consumer.consume())
            logger.debug("Received first message of topic '" + topic + "'")
            if not postgress_connector.table_exists(topic):
                postgress_connector.create_table(table_name=topic, data=first_message["data"])
                logger.info("Created table for topic '" + topic + "'")

            elif config["kafka-sink-postgres"]["database"]["update_colums_on_startup"]:
                number_of_added_columns = postgress_connector.update_columns(table_name=topic, data=first_message["data"])
                logger.info("Added " + str(number_of_added_columns) + " columns in table for topic '" + topic + "'")

            parsed_first_message_correctly = True
            try:
                postgress_connector.insert_values(table_name=topic, data=first_message)
            except psycopg2.OperationalError:
                exit(1)

        except (AssertionError, IndexError, avro.io.SchemaResolutionException):
            logger.warn("Could not parse first message of topic '" + topic + "'")

    # insertion loop
    logger.info("Starting insertion loop for topic '" + topic + "'...")
    for message in consumer:
        try:
            decoded_message = decode_message(message)
            logger.info("Received message from topic '" + topic + "' with offset " + str(message.offset) + " and timestamp " +
                        datetime.datetime.fromtimestamp(decoded_message["timestamp"]).strftime('%Y-%m-%d %H:%M:%S.%f'))
            try:
                postgress_connector.insert_values(table_name=topic, data=decoded_message)
            except psycopg2.OperationalError:
                exit(1)
        except (AssertionError, IndexError, avro.io.SchemaResolutionException):
            logger.warn("Could not parse message with offset " + str(message.offset) + " of topic '" + topic + "'")


if __name__ == '__main__':

    consumer_threads = list()

    client = KafkaClient(hosts=config["kafka"]["hosts"])

    for consumer_topic in config["kafka-sink-postgres"]["consumer"]["topics"]:

        simple_consumer = client.topics[str.encode(consumer_topic)].get_simple_consumer(
            consumer_group=str.encode(config["kafka-sink-postgres"]["consumer"]["consumer_group"]),
            auto_commit_enable=True,
            auto_commit_interval_ms=config["kafka-sink-postgres"]["consumer"]["auto_commit_interval"],
            use_rdkafka=config["kafka-sink-postgres"]["consumer"]["use_rdkafka"])

        consumer_threads.append(threading.Thread(target=loop_inserter, args=(simple_consumer,)))

    for i in range(0, len(consumer_threads)):
        logger.debug("Starting consumer thread #" + str(i))
        consumer_threads[i].start()

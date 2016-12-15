#!/usr/bin/env python3

import os
import logging.config
import signal
import io
import datetime
import threading
import avro.io
import psycopg2
from pykafka import KafkaClient

from connector import PostgresConnector

__author__ = "Stephan Müller"
__license__ = "MIT"


POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))
POSTGRES_DB = os.getenv("POSTGRES_DB", "postgres")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PW = os.getenv("POSTGRES_PW", "postgres")
KAFKA_HOSTS = os.getenv("KAFKA_HOSTS", "kafka:9092")
KAFKA_SCHEMA = os.getenv("KAFKA_SCHEMA", "/avro/schema/kafka.timestamp-data.avsc")
CONSUMER_GROUP = os.getenv("CONSUMER_GROUP", "postgres")
AUTO_COMMIT_INTERVAL = int(os.getenv("AUTO_COMMIT_INTERVAL", 60000))
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "")

logging_config_file = os.path.dirname(os.path.abspath(__file__)) + "logging.ini"
if os.path.isfile(logging_config_file):
    logging.config.fileConfig(logging_config_file)

logger = logging.getLogger('database_writer')
if LOGGING_LEVEL != "":
    logging.basicConfig(level=LOGGING_LEVEL)


# only way to handle SocketDisconnectedError exceptions and exit program by killing task with interrupt signal
# because os.exit() is not possible due to threading of pykafka
class ListenFilter(logging.Filter):
    def filter(self, record):
        if record.getMessage().startswith("Encountered SocketDisconnectedError"):
            logger.error("Lost connection to Kafka")
            os.kill(os.getpid(), signal.SIGINT)

        return True

logging.getLogger('pykafka.broker').addFilter(ListenFilter())
logging.getLogger('pykafka.cluster').addFilter(ListenFilter())

kafka_message_schema = avro.schema.Parse(open(KAFKA_SCHEMA, "rb").read().decode())

try:
    postgress_connector = PostgresConnector(host=POSTGRES_HOST, port=POSTGRES_PORT, database=POSTGRES_DB,
                                            user=POSTGRES_USER, password=POSTGRES_PW)
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
    logger.info("Waiting for first message of topic '" + topic + "'...")

    parsed_first_message_correctly = False
    while not parsed_first_message_correctly:
        try:
            # create or update table schema if necessary
            first_message = decode_message(consumer.consume())
            logger.info("Received first message of topic '" + topic + "'")
            if not postgress_connector.table_exists(topic):
                postgress_connector.create_table(table_name=topic, data=first_message["data"])
                logger.info("Created table for topic '" + topic + "'")

            else:
                number_of_added_columns = postgress_connector.update_columns(table_name=topic, data=first_message["data"])
                logger.info("Added " + str(number_of_added_columns) + " columns in table for topic '" + topic + "'")

            parsed_first_message_correctly = True
            try:
                postgress_connector.insert_values(table_name=topic, data=first_message)
            except psycopg2.OperationalError:
                exit(1)

        except (AssertionError, IndexError, avro.io.SchemaResolutionException):
            logger.warn("Could not parse first message of topic '" + topic + "'")

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


consumer_threads = list()

managed_topics = list()

client = KafkaClient(hosts=KAFKA_HOSTS)
for consumer_topic in client.topics:
    if consumer_topic not in managed_topics:

        simple_consumer = client.topics[consumer_topic].get_simple_consumer(
            consumer_group=str.encode(CONSUMER_GROUP),
            auto_commit_enable=True,
            auto_commit_interval_ms=AUTO_COMMIT_INTERVAL,
            use_rdkafka=True)

        consumer_threads.append(threading.Thread(target=loop_inserter, args=(simple_consumer,)))
        logger.info("Starting consumer thread #" + str(len(consumer_threads) - 1))
        consumer_threads[-1].start()

        managed_topics.append(consumer_topic)

for consumer_thread in consumer_threads:
    consumer_thread.join()

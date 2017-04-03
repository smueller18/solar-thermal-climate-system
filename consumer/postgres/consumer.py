#!/usr/bin/env python3

import os
import logging.config
import time


from confluent_kafka.avro import CachedSchemaRegistryClient
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
SCHEMA_REGISTRY_URL = os.getenv("SCHEMA_REGISTRY_URL", "http://localhost:8081")
CONSUMER_GROUP = os.getenv("CONSUMER_GROUP", "postgres")
ALLOWED_TOPICS_REGEX = os.getenv("ALLOWED_TOPICS_REGEX", ".*")
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")
logging_format = "%(levelname)8s %(asctime)s %(name)s [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"

logging.basicConfig(level=logging.getLevelName(LOGGING_LEVEL), format=logging_format)

logger = logging.getLogger('consumer')


schema_registry = CachedSchemaRegistryClient(url=SCHEMA_REGISTRY_URL)

postgres_connector = postgres.Connector(host=POSTGRES_HOST, port=POSTGRES_PORT, database=POSTGRES_DB,
                                         user=POSTGRES_USER, password=POSTGRES_PW)

topics = list()

def create_table_by_schema(topic):

    schema_registry.




def handle_message(msg):
    global postgres_connector

    # create table if not exists
    if not msg.topic().str() in topics:

        if not postgres_connector.table_exists(msg.topic().str()):
            create_table_by_schema(msg.topic().str())

        topics.append(msg.topic().str())





consumer = AvroLoopConsumer(KAFKA_HOSTS, SCHEMA_REGISTRY_URL, CONSUMER_GROUP, [ALLOWED_TOPICS_REGEX])
consumer.loop(lambda msg: handle_message(msg))





class DBWriter(object):
    def __init__(self, kafka_hosts, topic, kafka_message_schema_file, postgres_connector,
                 consumer_group=None, use_rdkafka=False, auto_commit_enable=True,
                 auto_commit_interval_ms=60000):

    def _new_message_handler(self, sender, message):

        try:
            if not self._parsed_first_message_correctly:
                # create or update table schema if necessary
                if not self._postgres_connector.table_exists(self._topic):
                    self._postgres_connector.create_table(table_name=self._topic, data=message["data"])
                    logger.info("Created table for topic '" + self._topic + "'")

                else:
                    number_of_added_columns = self._postgres_connector.update_columns(table_name=self._topic,
                                                                                      data=message["data"])
                    logger.info(
                        "Added " + str(number_of_added_columns) + " columns in table for topic '" + self._topic + "'")
                self._parsed_first_message_correctly = True

            self._postgres_connector.insert_values(table_name=self._topic, data=message)

        except psycopg2.OperationalError:
            raise ConnectionError("Postgres operational error.")

        except:
            # TODO not a nice way, because another exception is thrown
            self.join(0)



"""
postgress_connector = None

running = False
consumer_threads = list()
while True:
    if not running:
        consumer_threads = list()
        try:
            postgress_connector = PostgresConnector(host=POSTGRES_HOST, port=POSTGRES_PORT, database=POSTGRES_DB,
                                                    user=POSTGRES_USER, password=POSTGRES_PW)

            client = KafkaClient(hosts=KAFKA_HOSTS)
            for topic in client.topics:
                if re.search(ALLOWED_TOPICS_REGEX, topic.decode()) is not None:
                    thread = DBWriter(KAFKA_HOSTS, topic.decode(), CONSUMER_GROUP, KAFKA_SCHEMA,
                                      postgress_connector, use_rdkafka=False)
                    thread.start()
                    logger.info("Started consumer for topic " + topic.decode())
                    consumer_threads.append(thread)

            running = True

        except Exception as e:
            running = False
            for thread in consumer_threads:
                thread.join(0)
            logger.error(str(e))

        finally:
            time.sleep(30)

    else:
        while running:
            time.sleep(5)
            for thread in consumer_threads:
                if not thread.is_alive():
                    running = False
                    for thread in consumer_threads:
                        thread.join(0)
"""


#!/usr/bin/env python3

import os
import re
import logging.config
import time
from pykafka import KafkaClient

from pykafka_tools.postgres_connector import PostgresConnector
from pykafka_tools.kafka_consumer import DBWriter

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
KAFKA_SCHEMA = os.getenv("KAFKA_SCHEMA", __dirname__ + "/kafka.timestamp-data.avsc")
CONSUMER_GROUP = os.getenv("CONSUMER_GROUP", "postgres")
ALLOWED_TOPICS_REGEX = os.getenv("ALLOWED_TOPICS_REGEX", ".*")
LOGGING_INI = os.getenv("LOGGING_INI", __dirname__ + "/logging.ini")
logging_format = "%(levelname)8s %(asctime)s %(name)s [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"

if os.path.isfile(LOGGING_INI):
    logging.config.fileConfig(LOGGING_INI)
else:
    logging.basicConfig(level=logging.INFO, format=logging_format)

logger = logging.getLogger('database_writer')

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
                if re.search(ALLOWED_TOPICS_REGEX, topic) is not None:
                    thread = DBWriter(KAFKA_HOSTS, topic.decode(), CONSUMER_GROUP, KAFKA_SCHEMA,
                                      postgress_connector, auto_commit_interval_ms=AUTO_COMMIT_INTERVAL,
                                      use_rdkafka=False)
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
            time.sleep(5)

    else:
        while running:
            time.sleep(5)
            for thread in consumer_threads:
                if not thread.is_alive():
                    running = False
                    for thread in consumer_threads:
                        thread.join(0)

#!/usr/bin/env python3

# todo handle pykafka if logging Encountered SocketDisconnectedError while requesting metadata from broker
# destroy old consumer thread and start new one

import os
import datetime
import signal
import logging
import threading
from pykafka import KafkaClient
import avro.io
import io
import json
from flask import Flask

__author__ = "Stephan Müller"
__license__ = "MIT"

PORT = int(os.getenv("PORT", 5000))
KAFKA_HOSTS = os.getenv("KAFKA_HOSTS", "kafka:9092")
KAFKA_SCHEMA = os.getenv("KAFKA_SCHEMA", "/opt/config/kafka.avsc")
TOPIC = os.getenv("TOPIC", "chillii")
CONSUMER_GROUP = os.getenv("CONSUMER_GROUP", "monitor")
AUTO_COMMIT_INTERVAL = int(os.getenv("AUTO_COMMIT_INTERVAL", 60000))
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")
LOGGING_FORMAT = os.getenv("LOGGING_FORMAT", "%(message)s")


logging.basicConfig(format=LOGGING_FORMAT)
logger = logging.getLogger('app')
logger.setLevel(logging.getLevelName(LOGGING_LEVEL))


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

client = KafkaClient(hosts=KAFKA_HOSTS)
topic = client.topics[str.encode(TOPIC)]

latest_sensor_values_json = dict()


def kafka_consumer():
    global latest_sensor_values_json
    consumer = topic.get_simple_consumer(consumer_group=str.encode(CONSUMER_GROUP),
                                         auto_commit_enable=True,
                                         auto_commit_interval_ms=AUTO_COMMIT_INTERVAL,
                                         use_rdkafka=True)
    for message in consumer:
        try:
            bytes_reader = io.BytesIO(message.value)
            decoder = avro.io.BinaryDecoder(bytes_reader)
            reader = avro.io.DatumReader(kafka_message_schema)
            sensor_values = reader.read(decoder)
            latest_sensor_values_json = json.dumps(sensor_values)
            logger.debug("Received message with offset " + str(message.offset) + " and timestamp " +
                         datetime.datetime.fromtimestamp(sensor_values["timestamp"]).strftime('%Y-%m-%d %H:%M:%S.%f'))
        except Exception as e:
            logger.warn(e)


app = Flask(__name__)


@app.route('/')
def root():
    return app.send_static_file('index.html')


@app.route('/sensor_values.json')
def route_latest_sensor_values():
    return latest_sensor_values_json


@app.route('/sensor_description.json')
def route_sensor_description():
    return app.send_static_file('sensor_description.json')


@app.route('/<path:path>')
def static_proxy(path):
    return app.send_static_file(path)


def run():
    logger.info("Starting webserver at port " + str(PORT))
    app.run(host="0.0.0.0", port=PORT)


if __name__ == '__main__':
    webapp_thread = threading.Thread(target=run)
    consumer_thread = threading.Thread(target=kafka_consumer)

    webapp_thread.start()
    consumer_thread.start()

    webapp_thread.join()
    consumer_thread.join()

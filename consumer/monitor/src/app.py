#!/usr/bin/env python3

# todo handle pykafka if logging Encountered SocketDisconnectedError while requesting metadata from broker
# destroy old consumer thread and start new one

import os
import datetime
import argparse
import logging
import threading
import json
from pykafka import KafkaClient
import avro.io
import io
from flask import Flask

__author__ = "Stephan Müller"
__license__ = "MIT"


parser = argparse.ArgumentParser(
    description='Webserver which connects to Kafka and illustrates all available chillii sensor values on a plant '
                'visualization.')

parser.add_argument('-c', type=str, default="../config/config.json", help="config file")

args = parser.parse_args()
config_file = args.c

config = json.loads(open(config_file, "rb").read().decode())

logging.basicConfig(format=config["logging"]["format"])
logger = logging.getLogger('app')
logger.setLevel(logging.getLevelName(config["logging"]["level"]))

chillii_definition_file = config["chillii"]["device_definition_file"]
if not os.path.isabs(chillii_definition_file):
    chillii_definition_file = os.path.dirname(os.path.abspath(config_file)) + "/" + chillii_definition_file
chillii_definition = json.loads(open(chillii_definition_file, "rb").read().decode())

kafka_message_schema_file = config["kafka"]["message_schema_file"]
if not os.path.isabs(kafka_message_schema_file):
    kafka_message_schema_file = os.path.dirname(os.path.abspath(config_file)) + "/" + kafka_message_schema_file
kafka_message_schema = avro.schema.Parse(open(kafka_message_schema_file, "rb").read().decode())

client = KafkaClient(hosts=config["kafka"]["hosts"])
topic = client.topics[str.encode(config["web-monitoring"]["consumer"]["topic"])]

latest_sensor_values_json = dict()

sensor_description = dict()
for function in chillii_definition["function"]:
    for sensor_id in chillii_definition["function"][function]:
        if function.startswith("discrete"):
            sensor_description.update(
                {
                    sensor_id: {
                        "description": chillii_definition["function"][function][sensor_id]["description"],
                        "unit": ""
                    }
                 })

        if function.endswith("registers"):
            sensor_description.update(
                {
                    sensor_id: {
                        "description": chillii_definition["function"][function][sensor_id]["description"],
                        "unit": chillii_definition["function"][function][sensor_id]["unit"]
                    }
                 })
sensor_description_json = json.dumps(sensor_description)


def kafka_consumer():
    global latest_sensor_values_json
    consumer = topic.get_simple_consumer(consumer_group=str.encode(config["web-monitoring"]["consumer"]["consumer_group"]),
                                         auto_commit_enable=True,
                                         auto_commit_interval_ms=config["web-monitoring"]["consumer"]["auto_commit_interval"],
                                         use_rdkafka=config["web-monitoring"]["consumer"]["use_rdkafka"])
    for message in consumer:
        try:
            bytes_reader = io.BytesIO(message.value)
            decoder = avro.io.BinaryDecoder(bytes_reader)
            reader = avro.io.DatumReader(kafka_message_schema)
            sensor_values = reader.read(decoder)
            latest_sensor_values_json = json.dumps(sensor_values)
            logger.debug("Received message with offset " + str(message.offset) +  " and timestamp " +
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
    return sensor_description_json


@app.route('/<path:path>')
def static_proxy(path):
    return app.send_static_file(path)


def run():
    logger.info("Starting webserver on host " + config["web-monitoring"]["host"] + " at port " + str(config["web-monitoring"]["port"]))
    app.run(host=config["web-monitoring"]["host"], port=config["web-monitoring"]["port"])


if __name__ == '__main__':
    webapp_thread = threading.Thread(target=run)
    consumer_thread = threading.Thread(target=kafka_consumer)

    webapp_thread.start()
    consumer_thread.start()

    webapp_thread.join()
    consumer_thread.join()

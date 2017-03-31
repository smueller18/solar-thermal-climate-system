#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging.config
import time
import datetime

from pykafka_tools.kafka_consumer import KafkaConsumer
from pykafka_tools.kafka_producer_pool import KafkaProducerPool

from pysolar.solar import get_altitude, get_azimuth
from math import cos, sin, tan, radians

__author__ = u'Stephan Müller, Adrian Bürger, Andreas Klotz'
__copyright__ = u'2017, Stephan Müller, Adrian Bürger, Andreas Klotz'
__license__ = u'MIT'

__dirname__ = os.path.dirname(os.path.abspath(__file__))

KAFKA_HOSTS_CONSUMER = os.getenv("KAFKA_HOSTS_CONSUMER", "kafka:9092")
KAFKA_HOSTS_PRODUCER = os.getenv("KAFKA_HOSTS_PRODUCER", "kafka:9092")
KAFKA_SCHEMA = os.getenv("KAFKA_SCHEMA", __dirname__ + "/kafka.timestamp-data.avsc")
CONSUMER_GROUP = os.getenv("CONSUMER_GROUP", "solar_radiation")
CONSUMER_TOPIC = os.getenv("CONSUMER_TOPIC", "solar_radiation")
PRODUCER_TOPIC = os.getenv("PRODUCER_TOPIC", "solar_radiation_45_deg_angle")
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")
logging_format = "%(levelname)8s %(asctime)s %(name)s [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"

# Geographic coordinates of the K-building
LATITUDE_DEG = 49.01305
LONGITUDE_DEG = 8.39207
EVALUATION = 116.0

# Slope of the flat plate collectors
ALPHA = 45

# Orientation of the flat plate collectors (north=zero degree, clockwise positive)
BETA = 172

logging.basicConfig(level=logging.getLevelName(LOGGING_LEVEL), format=logging_format)

logger = logging.getLogger('rolling-median')

kafka_producer_pool = None


def compute_radiation_at_45_deg_angle(timestamp, total_radiation, diffuse_radiation):

    direct_radiation = total_radiation - diffuse_radiation

    # Pysolar: south is zero degree, clockwise negative, e.g. south east = - 315 degree, south west = -45 degree

    azimuth = get_azimuth(when=datetime.datetime.fromtimestamp(timestamp),
                          latitude_deg=LATITUDE_DEG, longitude_deg=LONGITUDE_DEG, elevation=EVALUATION)

    # In the calculation north is defined as zero degree, clockwise positive, the following conversion is required
    if azimuth < -180:
        azimuth = abs(azimuth) - 180
    else:
        azimuth = abs(azimuth) + 180

    altitude = get_altitude(when=datetime.datetime.fromtimestamp(timestamp),
                            latitude_deg=LATITUDE_DEG, longitude_deg=LONGITUDE_DEG, elevation=EVALUATION)

    # Formula from Lehrbuch der Bauphysik, Fischer, 2008, Page 651
    radiation_at_45_deg_angle = diffuse_radiation + direct_radiation * (cos(radians(ALPHA)) + sin(radians(ALPHA)) *
                                (cos(radians(azimuth - BETA)) / tan(radians(altitude))))

    return radiation_at_45_deg_angle


def handle_radiation_message(sender, message):
    radiation = compute_radiation_at_45_deg_angle(message["timestamp"],
                                                  message["data"]["total_radiation"],
                                                  message["data"]["diffuse_radiation"])

    kafka_producer_pool.produce(PRODUCER_TOPIC, {
        "timestamp": message["timestamp"],
        "data": {
            "solar_radiation_45_deg_angle": radiation
        }
    })


consumer_thread = None
started = False
while not started:
    try:
        # create producer
        kafka_producer_pool = KafkaProducerPool(KAFKA_HOSTS_PRODUCER, [PRODUCER_TOPIC], KAFKA_SCHEMA)

        # create consumer
        consumer_thread = KafkaConsumer(KAFKA_HOSTS_CONSUMER, CONSUMER_TOPIC, CONSUMER_GROUP, KAFKA_SCHEMA)
        consumer_thread.new_message_event += handle_radiation_message
        consumer_thread.start()
        logger.info("Started consumer thread for topic " + CONSUMER_TOPIC)

        started = True

    except Exception as e:
        logger.exception(e)
        time.sleep(30)

while True:
    time.sleep(100)

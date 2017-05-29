#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
import datetime

import kafka_connector.avro_loop_consumer as avro_loop_consumer
from kafka_connector.avro_loop_consumer import AvroLoopConsumer
from kafka_connector.avro_loop_producer import AvroLoopProducer

from pysolar.solar import get_altitude, get_azimuth
from math import cos, sin, tan, radians

__author__ = u'Stephan Müller, Adrian Bürger, Andreas Klotz'
__copyright__ = u'2017, Stephan Müller, Adrian Bürger, Andreas Klotz'
__license__ = u'MIT'

__dirname__ = os.path.dirname(os.path.abspath(__file__))

KAFKA_HOSTS = os.getenv("KAFKA_HOSTS", "kafka:9092")
SCHEMA_REGISTRY_URL = os.getenv("SCHEMA_REGISTRY_URL", "http://schema-registry:8082")
CONSUMER_GROUP = os.getenv("CONSUMER_GROUP", "solar_radiation")
CONSUMER_TOPIC = os.getenv("CONSUMER_TOPIC", "prod.stcs.roof.solar_radiation")
PRODUCER_TOPIC = os.getenv("PRODUCER_TOPIC", "prod.stcs.roof.solar_radiation_45_deg_angle")

LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")
logging_format = "%(levelname)8s %(asctime)s %(name)s [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"

key_schema = __dirname__ + "/config/key.avsc"
value_schema = __dirname__ + "/config/value.avsc"

# Geographic coordinates of the K-building
LATITUDE_DEG = 49.01305
LONGITUDE_DEG = 8.39207
EVALUATION = 116.0

# Slope of the flat plate collectors
ALPHA = 45

# Orientation of the flat plate collectors (north=zero degree, clockwise positive)
BETA = 172

logging.basicConfig(level=logging.getLevelName(LOGGING_LEVEL), format=logging_format)
logger = logging.getLogger('producer')


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

    # Formula from "Lehrbuch der Bauphysik, Fischer, 2008, Page 651"
    radiation_at_45_deg_angle = diffuse_radiation + direct_radiation * (cos(radians(ALPHA)) + sin(radians(ALPHA)) *
                                (cos(radians(azimuth - BETA)) / tan(radians(altitude))))

    if radiation_at_45_deg_angle < 0.0:

        radiation_at_45_deg_angle = 0.0
        

    return radiation_at_45_deg_angle


def handle_message(msg):
    radiation = compute_radiation_at_45_deg_angle(msg.key()["timestamp"] / 1000,
                                                  msg.value()["total_radiation"],
                                                  msg.value()["diffuse_radiation"])
    producer.produce(msg.key(), {"solar_radiation_45_deg_angle": radiation})


producer = AvroLoopProducer(KAFKA_HOSTS, SCHEMA_REGISTRY_URL, PRODUCER_TOPIC, key_schema, value_schema)

config = avro_loop_consumer.default_config
config['enable.auto.commit'] = False
config['default.topic.config'] = dict()
config['default.topic.config']['auto.offset.reset'] = 'largest'

consumer = AvroLoopConsumer(KAFKA_HOSTS, SCHEMA_REGISTRY_URL, CONSUMER_GROUP, [CONSUMER_TOPIC], config=config)
consumer.loop(lambda msg: handle_message(msg))

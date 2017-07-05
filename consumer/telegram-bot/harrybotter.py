#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
import telegram
import kafka_connector.avro_loop_consumer as avro_loop_consumer
from kafka_connector.avro_loop_consumer import AvroLoopConsumer

__author__ = u'Patrick Wiener, Adrian Bürger'
__copyright__ = u'2017, Patrick Wiener'
__license__ = u'MIT'

KAFKA_HOSTS = os.getenv("KAFKA_HOSTS", "kafka:9092")
SCHEMA_REGISTRY_URL = os.getenv("SCHEMA_REGISTRY_URL", "http://schema-registry:8082")
CONSUMER_GROUP = os.getenv("CONSUMER_GROUP", "telegram-bot")
TOPIC_PREFIX = os.getenv("TOPIC_PREFIX", "dev.stcs.cep.")
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

logging_format = "%(levelname)8s %(asctime)s %(name)s [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"

logging.basicConfig(level=logging.getLevelName(LOGGING_LEVEL), format=logging_format)
logger = logging.getLogger('telegram-cep-bot')

global bot
bot = telegram.Bot(token=TELEGRAM_TOKEN)


def cep_info_to_broadcast_message(cep_info):

    try:
        broadcast = str(cep_info["notificationType"]) + " at " + str(cep_info["startTime"]) + ": \n\n"

        if str(cep_info["isWarning"]) == "true":
            broadcast += "Warning: "
        else:
            broadcast += "All-clear: "

        broadcast += str(cep_info["notification"]) + "\n\n"
        broadcast += "Additional info provided for the event: \n\n"

        for key in cep_info.keys():
            if str(key) not in ["notificationType", "startTime", "isWarning", "notification"]:
                broadcast += str(key) + ": " + str(cep_info[key]) + "\n"

    except KeyError:
        logger.warning("Cannot parse CEP info dictionary, returning raw dictionary instead.")
        broadcast = str(cep_info)

    return broadcast


def broadcast_event_to_telegram(msg):

    if len(msg.value()) > 0:
        if type(msg.key()) is dict and "timestamp" in msg.key():

            timestamp = msg.key()["timestamp"] / 1000
            cep_info = msg.value()

            broadcast = cep_info_to_broadcast_message(cep_info)
            logger.info("Broadcasting message to telegram ...")

            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=broadcast)
            logger.info("Message sent.")


config = avro_loop_consumer.default_config
config['enable.auto.commit'] = True
config['default.topic.config'] = dict()
config['default.topic.config']['auto.offset.reset'] = 'latest'

consumer = AvroLoopConsumer(KAFKA_HOSTS, SCHEMA_REGISTRY_URL, CONSUMER_GROUP,
                            ["^" + TOPIC_PREFIX.replace(".", r'\.') + ".*"])
logger.info("Starting consumer thread ...")

try:
    consumer.loop(lambda msg: broadcast_event_to_telegram(msg))
except Exception as e:
    consumer.stop()
    raise e

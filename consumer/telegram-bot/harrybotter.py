#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
import telegram
import datetime
import kafka_connector.avro_loop_consumer as avro_loop_consumer
from kafka_connector.avro_loop_consumer import AvroLoopConsumer

__author__ = u'Patrick Wiener, Adrian Bürger'
__copyright__ = u'2017, Patrick Wiener'
__license__ = u'MIT'

KAFKA_HOSTS = os.getenv("KAFKA_HOSTS", "w-stcs-services:9092")
SCHEMA_REGISTRY_URL = os.getenv("SCHEMA_REGISTRY_URL", "http://w-stcs-services:8082")
CONSUMER_GROUP = os.getenv("CONSUMER_GROUP", "telegram-bot")
TOPIC_PREFIX = os.getenv("TOPIC_PREFIX", "dev.stcs.cep.")
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "370699713:AAF97jE7ruBPV9W-vgM1B9NVowVTL7aJvoM")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "-172083578")

logging_format = "%(levelname)8s %(asctime)s %(name)s [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"

logging.basicConfig(level=logging.getLevelName(LOGGING_LEVEL), format=logging_format)
logger = logging.getLogger('telegram-cep-bot')

bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)


def cep_info_to_broadcast_message(msg):

    cep_key = msg.key()
    cep_info = msg.value()

    try:

        broadcast = str(datetime.datetime.fromtimestamp(cep_key["startTime"] / 1000).replace(microsecond=0)) + ": *" \
                    + cep_info["notificationType"] + "*\n"

        broadcast += str(cep_info["notification"]) + "\n"

        for key in cep_info.keys():
            if str(key) not in ["isWarning", "notificationType", "notification"]:
                broadcast += "- " + str(key) + ": " + str(round(cep_info[key], 2)) + "\n"

    except KeyError:
        logger.warning("Cannot parse CEP info dictionary, returning raw dictionary instead.")
        broadcast = str(cep_info)

    return broadcast


def broadcast_cep_info_to_telegram(msg):

    if len(msg.value()) > 0:
        if type(msg.key()) is dict and "startTime" in msg.key():

            broadcast = cep_info_to_broadcast_message(msg)
            logger.info("Broadcasting message to telegram ...")

            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=broadcast, parse_mode=telegram.ParseMode.MARKDOWN)
            consumer.commit(msg, async=True)
            logger.info("Message sent.")


if (TELEGRAM_BOT_TOKEN is not None) and (TELEGRAM_CHAT_ID is not None):

    config = avro_loop_consumer.default_config
    config['enable.auto.commit'] = False
    config['default.topic.config'] = dict()
    config['default.topic.config']['auto.offset.reset'] = 'largest'

    consumer = AvroLoopConsumer(KAFKA_HOSTS, SCHEMA_REGISTRY_URL, CONSUMER_GROUP,
                                ["^" + TOPIC_PREFIX.replace(".", r'\.') + ".*"])
    logger.info("Starting consumer thread ...")

    try:
        consumer.loop(lambda msg: broadcast_cep_info_to_telegram(msg))
    except Exception as e:
        consumer.close()
else:
    logger.info("Set environment variables TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID.")
    exit()

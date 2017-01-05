# -*- coding: utf-8 -*-

import logging
import threading
import datetime
import time
import event
import io
import avro
from pykafka import KafkaClient

__author__ = u'Stephan Müller'
__copyright__ = u'2016, Stephan Müller'
__license__ = u'MIT'

logger = logging.getLogger(__name__)


class KafkaConsumer(threading.Thread):
    """A KafkaConsumer is a thread which consumes messages and notifies functions by an event trigger after every new
     consumption.
     """

    def __init__(self, kafka_hosts, topic, consumer_group, use_rdkafka=False, auto_commit_enable=True,
                 auto_commit_interval_ms=6000, kafka_message_schema=None):
        """
        Initializes a new instance

        :param kafka_hosts: kafka hosts
        :type kafka_hosts: str
        :param topic: topic for which a consumer should being created
        :type topic: str
        :param consumer_group: consumer group
        :type consumer_group: str
        :param use_rdkafka: set true to use rdkafka
        :type use_rdkafka: bool
        :param auto_commit_enable: enable auto commit
        :type auto_commit_enable: bool
        :param auto_commit_interval_ms: auto commit interval in milliseconds
        :type auto_commit_interval_ms: bool
        :param kafka_message_schema: kafka message schema
        :type kafka_message_schema: json string
        """

        super().__init__(name='KafkaConsumer_' + topic)
        self._stopevent = threading.Event()
        self._topic = topic
        self._consumer_group = consumer_group
        self._kafka_hosts = kafka_hosts
        self._use_rdkafka = use_rdkafka
        self._auto_commit_enable = auto_commit_enable
        self._auto_commit_interval_ms = auto_commit_interval_ms
        self._kafka_message_schema = kafka_message_schema

        self.sensor_values_update_event = event.Event()

    def get_topic(self):
        """
        Get topic name
        :return: topic name
        """
        return self._topic

    def run(self):
        """ Thread loop
        """

        while not self._stopevent.isSet():
            try:
                client = KafkaClient(hosts=self._kafka_hosts)
                topic = client.topics[str.encode(self._topic)]
                consumer = topic.get_simple_consumer(consumer_group=str.encode(self._consumer_group),
                                                     auto_commit_enable=self._auto_commit_enable,
                                                     auto_commit_interval_ms=self._auto_commit_interval_ms,
                                                     use_rdkafka=self._use_rdkafka)
                for message in consumer:
                    try:
                        if self._stopevent.isSet():
                            raise InterruptedError

                        if self._kafka_message_schema is None:
                            self.sensor_values_update_event.fire(self, message.value)

                        else:
                            bytes_reader = io.BytesIO(message.value)
                            decoder = avro.io.BinaryDecoder(bytes_reader)
                            reader = avro.io.DatumReader(self._kafka_message_schema)
                            sensor_values = reader.read(decoder)
                            logger.info("Received message with offset " + str(message.offset) + " and timestamp " +
                                        datetime.datetime.fromtimestamp(sensor_values["timestamp"]).strftime('%Y-%m-%d %H:%M:%S.%f'))

                            self.sensor_values_update_event.fire(self, sensor_values)

                    except Exception as e:
                        logger.error(e)

            except Exception as e:
                logger.error(e)
                time.sleep(1)

    def join(self, timeout=None):
        """
        Stop the thread loop and wait for it to end.

        :param timeout: timeout
        """
        self._stopevent.set()
        threading.Thread.join(self, timeout)

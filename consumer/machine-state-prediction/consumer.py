#!/usr/bin/env python3

import os
import time
import logging.config
import pickle
import pandas as pd
from pca import PCAForPandas

import kafka_connector.avro_loop_consumer as avro_loop_consumer
from kafka_connector.avro_loop_consumer import AvroLoopConsumer

from tsfresh.feature_extraction import extract_features
from tsfresh.feature_extraction import settings


__author__ = u'Stephan Müller'
__copyright__ = u'2017, Stephan Müller'
__license__ = u'MIT'

__dirname__ = os.path.dirname(os.path.abspath(__file__))


KAFKA_HOSTS = os.getenv("KAFKA_HOSTS", "kafka:9092")
SCHEMA_REGISTRY_URL = os.getenv("SCHEMA_REGISTRY_URL", "http://schema-registry:8082")
CONSUMER_GROUP = os.getenv("CONSUMER_GROUP", "postgres")
TOPIC_NAME = os.getenv("TOPIC_NAME", "prod.machine_learning.aggregations_10minutes")


SHOW_CALCULATION_TIME = int(os.getenv("SHOW_CALCULATION_TIME", 0))
# Dict with column names
FC_PARAMETERS = os.getenv("FC_PARAMETERS", __dirname__ + "/data/fc-parameters.pkl")
# PCAForPandas object
PCA_MODEL = os.getenv("PCA_MODEL", __dirname__ + "/data/pca-model.pkl")
# ML model with predict function
ML_MODEL = os.getenv("ML_MODEL", __dirname__ + "/data/ml-model.pkl")

LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")
logging_format = "%(levelname)8s %(asctime)s %(name)s [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"

logging.basicConfig(level=logging.getLevelName(LOGGING_LEVEL), format=logging_format)

logger = logging.getLogger('consumer')


with open(FC_PARAMETERS, 'rb') as f:
    fc_parameters = pickle.load(f)

with open(PCA_MODEL, 'rb') as f:
    pca_model = pickle.load(f)

with open(ML_MODEL, 'rb') as f:
    ml_model = pickle.load(f)


def handle_message(msg):

    if msg.key() is None or type(msg.key()) is not dict:
        logger.warning("Key is none. Ignoring message.")
        return
    elif msg.value() is None or type(msg.value()) is not dict:
        logger.warning("Value is none. Ignoring message.")
        return

    try:
        time_begin = time.time()

        timeseries = pd.melt(pd.DataFrame.from_dict(msg.value(), orient='index').transpose()).dropna()
        timeseries['group_id'] = 0

        if timeseries.isnull().sum().sum() > 0:
            logger.warning("at least one field of timeseries is null")
            return

        X = extract_features(timeseries, column_id='group_id', column_kind="variable", column_value="value",
                             kind_to_fc_parameters=settings.from_columns(fc_parameters), disable_progressbar=False)

        if X.isnull().sum().sum() > 0:
            logger.warning("at least one field of extracted features is null")
            return

        kritisch = ml_model.predict(pca_model.transform(X))[0]

        time_end = time.time()

        start_prediction_interval = time.localtime(msg.key()['timestamp_end'] / 1000)
        end_prediction_interval = time.localtime(msg.key()['timestamp_end'] / 1000 + 60*5)

        print("Prediction for interval",
              time.strftime("%H:%M:%S", start_prediction_interval),
              "to",
              time.strftime("%H:%M:%S", end_prediction_interval),
              ":",
              "kritisch" if kritisch else "unkritisch"
              )

        if SHOW_CALCULATION_TIME == 1:
            print("time for calculation", round(time_end - time_begin, 5), "seconds")

    except Exception as e:
        logger.exception(e)
        consumer.stop()


config = avro_loop_consumer.default_config
config['enable.auto.commit'] = True
config['default.topic.config'] = dict()
config['default.topic.config']['auto.offset.reset'] = 'end'


consumer = AvroLoopConsumer(KAFKA_HOSTS, SCHEMA_REGISTRY_URL, CONSUMER_GROUP, [TOPIC_NAME], config=config)
consumer.loop(lambda msg: handle_message(msg))

# rolling-median
This app consumes all messages for elected Kafka topics calculates rolling median and produce them under a new topic.

## How to prepare
Required libraries:

- python3

Required non-standard python packages:
- avro-python3
- pykafka
- pykafka-tools

Install all required libraries and python packages.

## Getting started
First, clone this project to your local PC. Then, you can run `rolling_median.py`. For parameterization, environment variables are used.
```
$ git clone https://github.com/smueller18/solar-thermal-climate-system.git
$ cd solar-thermal-climate-system/producer/rolling-median/src/
$ python3 rolling_median.py
```
Here is a list of all variables which can be set by environment variables. `__dirname__` is a placeholder for the absolute path to the directory of `rolling_median.py`.

| variable | default | type | info |
| --- | --- | --- | --- |
| PORT | 5001 | int | port of REST server |
| KAFKA_HOSTS_CONSUMER | kafka:9092 | string |   |
| KAFKA_HOSTS_PRODUCER | kafka:9092 | string |   |
| KAFKA_SCHEMA | /avro/schema/kafka.timestamp-data.avsc | string |   |
| CONSUMER_GROUP | rolling-median | string |   |
| ROLLING_MEDIAN_WINDOW | 5 | int |   |
| ALLOWED_TOPICS_REGEX_CONSUMER | .* | regex | .* means handle all topics |
| TOPIC_SUFFIX_PRODUCER | _rolling_median | string | produce topic is consumer topic + this suffix |
| LOGGING_INI | `__dirname__` + "/logging.ini" | string | preferrably use absolute path |

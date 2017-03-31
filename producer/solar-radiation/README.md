# producer-solar-radiation
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
First, clone this project to your local PC. Then, you can run `producer.py`. For parameterization, environment variables are used.
```
$ git clone https://github.com/smueller18/solar-thermal-climate-system.git
$ cd solar-thermal-climate-system/producer/solar-radiation
$ python3 producer.py
```
Here is a list of all variables which can be set by environment variables. `__dirname__` is a placeholder for the absolute path to the directory of `producer.py`.

| variable | default | type | info |
| --- | --- | --- | --- |
| PORT | 5001 | int | port of REST server |
| KAFKA_HOSTS_CONSUMER | kafka:9092 | string |   |
| KAFKA_HOSTS_PRODUCER | kafka:9092 | string |   |
| KAFKA_SCHEMA | /avro/schema/kafka.timestamp-data.avsc | string |   |
| CONSUMER_GROUP | solar_radiation | string |   |
| CONSUMER_TOPIC | solar_radiation | string |   |
| PRODUCER_TOPIC | solar_radiation_45_deg_angle | string |   |
| LOGGING_LEVEL | INFO | string | one of CRITICAL, ERROR, WARNING, INFO, DEBUG |

# producer-solar-radiation

Within the application, the current effective solar irradiance on the inclined surface of a solar collectors is calculated using the measured solar irradiance at normal incidence and the solar azimuth and altitude angles. In our case, the surface of the observed solar collectors is tilted by 45 degrees and rotated counter-clockwise from south by 8 degrees.

## How to prepare
Required libraries:

- python3
- librdkafka

Required non-standard python packages:
- avro-python3
- confluent_kafka
- kafka_connector
- json
- jsonschema
- pysolar

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

# cache-rest
This app consumes all messages for all available Kafka topics and provides latest sensor values by REST interface.

## How to prepare
Required libraries:

- python3

Required non-standard python packages:
- json
- avro-python3
- pykafka
- flask

Install all required libraries and python packages.

## Getting started
First, clone this project to your local PC. Then, you can run `app.py`. For parameterization, environment variables are used.
```
$ git clone https://github.com/smueller18/solar-thermal-climate-system.git
$ cd solar-thermal-climate-system/consumer/cache-rest/src/
$ python3 app.py
```
Here is a list of all variables which can be set by environment variables. `__dirname__` is a placeholder for the absolute path to the directory of `app.py`.

| variable | default | type | info |
| --- | --- | --- | --- |
| PORT | 5001 | int | port of REST server |
| KAFKA_HOSTS | kafka:9092 | string |   |
| KAFKA_SCHEMA | /avro/schema/kafka.timestamp-data.avsc | string |   |
| CONSUMER_GROUP | postgres | string |   |
| AUTO_COMMIT_INTERVAL | 60000 | int | milliseconds |
| LOGGING_INI | `__dirname__` + "/logging.ini" | string | preferrably use absolute path |

## Timing
The global timestamp is set to the latest timestamp of all consumed messages. Therefore it is possible that not all sensor values have the same time stamp and it could be that there are older than given global timestamp.

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
- pykafka-tools

Install all required libraries and python packages.

## Getting started
First, clone this project to your local PC. Then, you can run `consumer_cache_rest.py`. For parameterization, environment variables are used.
```
$ git clone https://github.com/smueller18/solar-thermal-climate-system.git
$ cd solar-thermal-climate-system/consumer/cache-rest/src/
$ python3 consumer_cache_rest.py
```
Here is a list of all variables which can be set by environment variables. `__dirname__` is a placeholder for the absolute path to the directory of `consumer_cache_rest.py`.

| variable | default | type | info |
| --- | --- | --- | --- |
| PORT | 5001 | int | port of REST server |
| KAFKA_HOSTS | kafka:9092 | string |   |
| KAFKA_SCHEMA | `__dirname__` + "/kafka.timestamp-data.avsc" | string |   |
| CONSUMER_GROUP | cache-rest | string |   |
| ALLOWED_TOPICS_REGEX | .* | string | .* means handle all topics |
| LOGGING_LEVEL | INFO | string | one of CRITICAL, ERROR, WARNING, INFO, DEBUG |

## Timing
The global timestamp is set to the latest timestamp of all consumed messages. Therefore it is possible that not all sensor values have the same time stamp and it could be that there are older than given global timestamp.

## API
For the API description have a look at [API.md](API.md).
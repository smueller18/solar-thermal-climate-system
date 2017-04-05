# consumer-socketio
This app consumes all messages for all available Kafka topics and mirrors them to through a SocketIO server.

## How to prepare
Required libraries:

- python3

Required non-standard python packages:
- avro-python3
- flask
- flask_socketio
- confluent_kafka
- kafka_connector

Install all required libraries and python packages.

## Getting started
First, clone this project to your local PC. Then, you can run `consumer.py`. For parametrization, environment variables are used.
```
$ git clone https://github.com/smueller18/solar-thermal-climate-system.git
$ cd solar-thermal-climate-system/consumer/socketio
$ python3 consumer.py
```
Here is a list of all variables which can be set by environment variables. `__dirname__` is a placeholder for the absolute path to the directory of `consumer.py`.

| variable | default | type | info |
| --- | --- | --- | --- |
| PORT | 5002 | int | port of SocketIO server |
| KAFKA_HOSTS | kafka:9092 | string |   |
| SCHEMA_REGISTRY_URL | http://schema-registry:8082 | string |   |
| CONSUMER_GROUP | web-redirect | string |   |
| TOPIC_PREFIX | stcs. | string |  |
| LOGGING_LEVEL | INFO | string | one of CRITICAL, ERROR, WARNING, INFO, DEBUG |

## API
For the API description have a look at [API.md](API.md).

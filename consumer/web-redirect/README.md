# consumer-web-redirect
This app consumes all messages for all available Kafka topics and mirrors them to through a SocketIO server.

## How to prepare
Required libraries:

- python3

Required non-standard python packages:
- avro-python3
- pykafka
- flask
- flask_socketio
- pykafka-tools

Install all required libraries and python packages.

## Getting started
First, clone this project to your local PC. Then, you can run `consumer.py`. For parametrization, environment variables are used.
```
$ git clone https://github.com/smueller18/solar-thermal-climate-system.git
$ cd solar-thermal-climate-system/consumer/web-redirect
$ python3 consumer.py
```
Here is a list of all variables which can be set by environment variables. `__dirname__` is a placeholder for the absolute path to the directory of `consumer.py`.

| variable | default | type | info |
| --- | --- | --- | --- |
| PORT | 5002 | int | port of SocketIO server |
| KAFKA_HOSTS | kafka:9092 | string |   |
| KAFKA_SCHEMA | `__dirname__` + "/kafka.timestamp-data.avsc" | string |   |
| CONSUMER_GROUP | web-redirect | string |   |
| ALLOWED_TOPICS_REGEX | .* | string | .* means handle all topics |
| LOGGING_LEVEL | INFO | string | one of CRITICAL, ERROR, WARNING, INFO, DEBUG |

## API
For the API description have a look at [API.md](API.md).

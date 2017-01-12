# cache-rest
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
First, clone this project to your local PC. Then, you can run `consumer_web_redirect.py`. For parametrization, environment variables are used.
```
$ git clone https://github.com/smueller18/solar-thermal-climate-system.git
$ cd solar-thermal-climate-system/consumer/web-redirect/src/
$ python3 consumer_web_redirect.py
```
Here is a list of all variables which can be set by environment variables. `__dirname__` is a placeholder for the absolute path to the directory of `consumer_web_redirect.py`.

| variable | default | type | info |
| --- | --- | --- | --- |
| PORT | 5002 | int | port of SocketIO server |
| KAFKA_HOSTS | kafka:9092 | string |   |
| KAFKA_SCHEMA | `__dirname__` + "/kafka.timestamp-data.avsc" | string |   |
| CONSUMER_GROUP | web-redirect | string |   |
| ALLOWED_TOPICS_REGEX | .* | string | .* means handle all topics |
| LOGGING_LEVEL | INFO | string | one of CRITICAL, ERROR, WARNING, INFO, DEBUG |

## API
**Event**: sensor_values_cache<br>
After a client connected, this event is used to push all latest available Kafka messages. For each topic. a separate message is send. The cache can be used if there are (temporarily) no producers available for a topic. The structure of the websocket messages are as follows:
```json
{
  "topic": <topic>,
  "timestamp": <timestamp>,
  "data": {
    "sensorId1": <value>,
    "sensorId2": <value>,
    ...
  }
}
```

**Event**: sensor_values<br>
This is a broadcast event which is send to all connected clients as soon as a new Kafka message arrives. The structure of the websocket messages are as follows:
```json
{
  "topic": <topic>,
  "timestamp": <timestamp>,
  "data": {
    "sensorId1": <value>,
    "sensorId2": <value>,
    ...
  }
}
```
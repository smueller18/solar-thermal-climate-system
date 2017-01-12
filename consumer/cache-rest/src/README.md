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

## Defaults
If no values are received via Kafka, the default values of the REST interface will be
```json
{
  "timestamp": 0,
  "data": {}
}
```
For checking if values exist, simply check for `timestamp == 0`.

## API
If an error occurred, an error message is send as follows:
```json
{
  "error": "<error>"
}
```

**Location**: `/topics`<br>
Returns most recent sensor data for all available topics. The structure of the responses is as follows:
```json
{
  "<topic1>": {
    "timestamp": <timestamp>,
    "data": {
      "sensorId1": <value>,
      "sensorId2": <value>,
      ...
    }  
  },
  ...
}
```

**Location**: `/topic/<topic>`<br>
Returns most recent sensor data for the selected topic. The structure of the responses is as follows:
```json
{
  "<topic1>": {
    "timestamp": <timestamp>,
    "data": {
      "sensorId1": <value>,
      "sensorId2": <value>,
      ...
    }  
  },
  ...
}
```
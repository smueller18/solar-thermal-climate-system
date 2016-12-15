# cache-rest
This app consumes all messages for topic `chillii` and provides latest sensor values by REST interface.

## How to prepare
Required libraries:

- python3
- librdkafka

Required python packages:
- os
- logging
- signal
- io
- datetime
- threading
- json
- avro-python3
- pykafka
- flask

Install all required libraries and python packages.

## How to use
First, clone this project to your local PC. Then, you can run `app.py`.
```
$ git clone https://github.com/smueller18/solar-thermal-climate-system/tree/master/consumer/cache-rest/src
$ cd solar-thermal-climate-system/consumer/cache-rest/src/
$ python3 app.py
```
Here is a list of all variables which can be set by environment variables.

| variable | default | type | info |
| --- | --- | --- | --- |
| PORT | 5001 | int | port of REST server |
| KAFKA_HOSTS | kafka:9092 | string |   |
| KAFKA_SCHEMA | /avro/schema/kafka.timestamp-data.avsc | string |   |
| CONSUMER_GROUP | postgres | string |   |
| AUTO_COMMIT_INTERVAL | 60000 | int | milliseconds |

## Exception handling
If connection to broker is lost, `collector.py` will be terminated.

## Timing
The time of sensor values is set to the time before the function to read the values over modbus is called.

## Chillii System Controller modbus definition
Define all available sensor addresses in `config/modbus_chillii_definition.json`. To see how the information must be provided have a look at the related schema `config/modbus_device_definition.schema.json`.

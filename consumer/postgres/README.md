# kafka-sink-postgres
This app consumes all kafka topics and stores the values in the database. After creating new topics, restart this application and a table will be generated automatically.

## How to prepare
Required libraries:

- python3
- postgresql-dev
- librdkafka

Required python packages:
- os
- logging
- signal
- io
- datetime
- threading
- avro-python3
- psycopg2
- pykafka

Install all required libraries and python packages.

## How to use
First, clone this project to your local PC. Then, you can run `database_writer.py`.
```
$ git clone https://github.com/smueller18/solar-thermal-climate-system/tree/master/consumer/postgres/src
$ cd solar-thermal-climate-system/consumer/postgres/src/
$ python3 database_writer.py
```
Here is a list of all variables which can be set by environment variables.

| variable | default | type | info |
| --- | --- | --- | --- |
| POSTGRES_HOST | postgres | string |   |
| POSTGRES_PORT | 5432 | int |   |
| POSTGRES_DB | postgres | string |   |
| POSTGRES_USER | postgres | string |   |
| POSTGRES_PW | postgres | string |   |
| KAFKA_HOSTS | kafka:9092 | string |   |
| KAFKA_SCHEMA | /avro/schema/kafka.timestamp-data.avsc | string | use absolute paths |
| CONSUMER_GROUP | cache-rest | string |   |
| AUTO_COMMIT_INTERVAL | 60000 | int | milliseconds |

## Exception handling
If connection to broker is lost, `collector.py` will be terminated.

## Timing
The time of sensor values is set to the time before the function to read the values over modbus is called.

## Chillii System Controller modbus definition
Define all available sensor addresses in `config/modbus_chillii_definition.json`. To see how the information must be provided have a look at the related schema `config/modbus_device_definition.schema.json`.

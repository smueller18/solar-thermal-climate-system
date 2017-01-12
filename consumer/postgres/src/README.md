# kafka-sink-postgres
This app consumes all kafka topics and stores the values in the database. After creating new topics, restart this application and a table will be generated automatically.

## How to prepare
Required libraries:

- python3
- postgresql-dev
- librdkafka

Required non-standard python packages:
- avro-python3
- psycopg2
- pykafka

Install all required libraries and python packages.

## Getting started
First, clone this project to your local PC. Then, you can run `consumer_postgres.py`. For parameterization, environment variables are used.
```
$ git clone https://github.com/smueller18/solar-thermal-climate-system.git
$ cd solar-thermal-climate-system/consumer/postgres/src/
$ python3 consumer_postgres.py
```
Here is a list of all variables which can be set by environment variables. `__dirname__` is a placeholder for the absolute path to the directory of `consumer_postgres.py`.

| variable | default | type | info |
| --- | --- | --- | --- |
| POSTGRES_HOST | postgres | string |   |
| POSTGRES_PORT | 5432 | int |   |
| POSTGRES_DB | postgres | string |   |
| POSTGRES_USER | postgres | string |   |
| POSTGRES_PW | postgres | string |   |
| KAFKA_HOSTS | kafka:9092 | string |   |
| KAFKA_SCHEMA | `__dirname__` + "/kafka.timestamp-data.avsc" | string |   |
| CONSUMER_GROUP | postgres | string |   |
| ALLOWED_TOPICS_REGEX | .* | string | .* means handle all topics |
| LOGGING_LEVEL | INFO | string | one of CRITICAL, ERROR, WARNING, INFO, DEBUG |

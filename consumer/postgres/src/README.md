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
First, clone this project to your local PC. Then, you can run `database_writer.py`. For parameterization, environment variables are used.
```
$ git clone https://github.com/smueller18/solar-thermal-climate-system.git
$ cd solar-thermal-climate-system/consumer/postgres/src/
$ python3 database_writer.py
```
Here is a list of all variables which can be set by environment variables. `__dirname__` is a placeholder for the absolute path to the directory of `database_writer.py`.

| variable | default | type | info |
| --- | --- | --- | --- |
| POSTGRES_HOST | postgres | string |   |
| POSTGRES_PORT | 5432 | int |   |
| POSTGRES_DB | postgres | string |   |
| POSTGRES_USER | postgres | string |   |
| POSTGRES_PW | postgres | string |   |
| KAFKA_HOSTS | kafka:9092 | string |   |
| KAFKA_SCHEMA | \_\_dirname\_\_ + "/kafka.timestamp-data.avsc" | string |   |
| CONSUMER_GROUP | cache-rest | string |   |
| AUTO_COMMIT_INTERVAL | 60000 | int | milliseconds |
| ALLOWED_TOPICS_REGEX | .* | string | .* means handle all topics |
| LOGGING_INI | `__dirname__` + "/logging.ini" | string | preferrably use absolute path |

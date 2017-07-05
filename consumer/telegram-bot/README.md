# telegram-bot
This app consumes all CEP notifications for CEP-related Kafka topics and sends them to a private [Telegram](https://telegram.org/) chat.

## How to prepare
Required libraries:

- python3

Required non-standard python packages:
- kafka_connector
- python-telegram-bot

Install all required libraries and python packages.

## Getting started
First, clone this project to your local PC. Then, you can run `harrybotter.py`. For parameterization, environment variables are used.
```
$ git clone https://github.com/smueller18/solar-thermal-climate-system.git
$ cd solar-thermal-climate-system/consumer/telegram-bot
$ python3 harrybotter.py
```
Here is a list of all variables which can be set by environment variables.

| variable | default | type | info |
| --- | --- | --- | --- |
| KAFKA_HOSTS | kafka:9092 | string |   |
| SCHEMA_REGISTRY_URL | http://schema-registry:8082 | string |  |
| CONSUMER_GROUP | telegram-bot | string |   |
| TOPIC_PREFIX | dev.stcs.cep.* | string | .* means handle all cep topics |
| LOGGING_LEVEL | INFO | string | one of CRITICAL, ERROR, WARNING, INFO, DEBUG |
| **TELEGRAM_BOT_TOKEN** | -  | string  | **MANDATORY** to be set |
| **TELEGRAM_CHAT_ID** | -  | string  | **MANDATORY** to be set |

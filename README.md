# Solar Thermal Climate System

Docker containers for the solar thermal climate system project at Karlsruhe University of Applied Sciences.

## Requirements

- docker-compose >= 1.9.0
- docker >= 1.11

## Running

If your config folder is not located at `../config`, then set `STCS_CONFIG_FOLDER` environment variable:
```
export STCS_CONFIG_FOLDER="YOUR_PATH"
```

Run `docker-compose up -d --build` in root folder to build all consumer and producer containers and to start all containers.


## Kafka Topics

The notation of a Kafka topic is devided in at least 3 parts: `<main_prefix>.<sub_prefix>.<source>`,
where `<main_prefix>` is one of `prod` for production, `dev` for development and `test` for testing purposes. `<sub_prefix>` refers to the related system, in this case always use `stcs`. `<source>` can be devided in more parts, seperated by dots. If the sensors related to a topic are all at the same place, use the notation `<place>.<sensor_type>`.

An example:
```
prod.stcs.atrium.temperatures
```

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

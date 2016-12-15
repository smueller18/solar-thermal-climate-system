# solar-thermal-climate-system

## Requirements

- docker-compose >= 1.9.0

## Running

If your config folder is not located at `../config`, then set `STCS_CONFIG_FOLDER` environment variable:
```
export STCS_CONFIG_FOLDER="YOUR_PATH"
```

Run `docker-compose up -d` in root folder to start all containers.

## Alerts
- After changeing app files of folders `./consumer`, a rebuild of docker-compose is necessary with `docker-compose build`.
- It could happen, that containers are stopped and started with a new IP address while nginx is running. In this case, the upstream links to the old container IP. For this reason, nginx has to be reloaded.

.SILENT:

default: help

build:

	docker-compose build

clean: ## remove all unnecessary volumes and the created network
	docker rm -v $$(docker ps --filter status=exited -q 2>/dev/null) 2>/dev/null
	docker volume rm $$(docker volume ls -qf dangling=true -q 2>/dev/null) 2>/dev/null
	docker network rm stcs 2>/dev/null

start: export USER_ID = $(shell id -u $$USER)
start: ## docker compose start
	docker-compose start

stop: export USER_ID = $(shell id -u $$USER)
stop: ## docker compose stop
	docker-compose stop

up:
	export USER_ID = $(shell id -u $$USER)
up:
	docker network create -d bridge stcs
	docker-compose up -d

help :
	echo "make [target]"
	echo ""
	echo "build		builds docker images"
	echo "start		starts all stopped containers"
	echo "stop		stops all running containers"
	echo "up			creates stcs network and launches multi-container services"
	echo ""

APP_NAME = atra_bot

default: up

up:
	docker-compose up --build

up-background:
	docker-compose up -d --build

shell:
	docker exec -it ${APP_NAME} bash

rebuild:
	docker-compose build --no-cache

restart:
	docker-compose down && docker-compose up --build
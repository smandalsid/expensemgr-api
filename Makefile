-include .env
export

build:
	docker compose down
	docker compose up --build 'app'

run:
	docker start docker-fastapi-app-db
	docker start fastapi-app

stop:
	docker stop fastapi-app
	docker stop docker-fastapi-app-db

test:
	docker compose down
	docker compose up --build 'app-test'

ims:
	docker images

cons:
	docker ps -a
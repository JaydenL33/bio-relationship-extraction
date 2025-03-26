.PHONY: build up shell stop

build:
	docker compose build

up:
	docker compose up -d

shell:
	docker compose run --rm llm_dev bash

stop:
	docker compose down
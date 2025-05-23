.PHONY: up stop

up:
	docker compose up -d
stop:
	docker compose down
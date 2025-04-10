.PHONY: kafka
kafka:
	docker-compose -f docker-compose.kafka.yml up --build

.PHONY: search
search:
	docker-compose -f docker-compose.search.yml up --build

.PHONY: search_without_service
search_without_service:
	docker-compose -f docker-compose.search.yml up elasticsearch redis --build

.PHONY: startup
startup: kafka search ;
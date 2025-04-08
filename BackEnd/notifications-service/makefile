test:
	docker compose -f .\docker-compose.notifications.yml run --rm scala-mail-service sbt test

test-clean:
	docker compose -f .\docker-compose.notifications.yml run --rm scala-mail-service sbt clean test

run:
	docker compose -f ..\..\docker-compose.kafka.yml up --build -d && \
	docker compose -f .\docker-compose.notifications.yml up --build -d


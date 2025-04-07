#!/bin/bash
set -e

echo "Starting Debezium Connect..."
/docker-entrypoint.sh start &

sleep 20

echo "Waiting for Debezium Connect API..."
until curl -s http://localhost:8083/connectors > /dev/null; do
  sleep 5
done
echo "Debezium Connect API is available."

# Create event service debezium connector if not exists
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8083/connectors/event-connector | grep -q "404"; then
  sleep 5
  echo "Connector event-connector not found. Creating connector..."
  curl -X POST -H "Content-Type: application/json" --data '{
    "name": "event-connector",
    "config": {
      "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
      "plugin.name": "pgoutput",
      "database.hostname": "'"${POSTGRES_HOST}"'",
      "database.port": "'"${POSTRGRES_DB_HOST_PORT}"'",
      "database.user": "'"${POSTGRES_USER}"'",
      "database.password": "'"${POSTGRES_PASSWORD}"'",
      "database.dbname": "'"${POSTGRES_DB}"'",
      "database.server.name": "event-connector",
      "table.include.list": "public.events",
      "slot.name": "events_slot",
      "snapshot.mode": "initial",
      "key.converter": "io.confluent.connect.avro.AvroConverter",
      "key.converter.schema.registry.url": "http://schema-registry:8081",
      "value.converter": "io.confluent.connect.avro.AvroConverter",
      "value.converter.schema.registry.url": "http://schema-registry:8081"
    }
  }' http://localhost:8083/connectors
  echo "Connector event-connector created."
else
  echo "Connector event-connector already exists. Skipping creation."
fi

# Create news service debezium connector if not exists
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8083/connectors/news-connector | grep -q "404"; then
  echo "Connector news-connector not found. Creating connector..."
  curl -X POST -H "Content-Type: application/json" --data '{
    "name": "news-connector",
    "config": {
      "connector.class": "io.debezium.connector.mongodb.MongoDbConnector",
      "tasks.max": "1",
      "mongodb.name": "news-connector",
      "mongodb.hosts": "'"${MONGODB_HOSTS}"'",
      "mongodb.user": "'"${MONGODB_USER}"'",
      "mongodb.password": "'"${MONGODB_PASSWORD}"'",
      "mongodb.authSource": "'"${MONGODB_AUTH_SOURCE}"'",
      "database.include.list": "news",
      "collection.include.list": "news.NewsModel",
      "snapshot.mode": "initial",
      "key.converter": "io.confluent.connect.avro.AvroConverter",
      "key.converter.schema.registry.url": "http://schema-registry:8081",
      "value.converter": "io.confluent.connect.avro.AvroConverter",
      "value.converter.schema.registry.url": "http://schema-registry:8081"
    }
  }' http://localhost:8083/connectors
  echo "Connector news-connector created."
else
  echo "Connector news-connector already exists. Skipping creation."
fi

wait
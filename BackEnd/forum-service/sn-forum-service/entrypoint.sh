#!/bin/sh

echo "Waiting for Cassandra to be ready..."

apt-get update && apt-get install -y netcat-openbsd


until nc -z cassandra 9042; do
  echo "Cassandra is not ready yet, waiting..."
  sleep 5
done

sleep 10

echo "Cassandra is ready, starting the application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
#!/bin/bash
set -e

ES_HOST="${ELASTICSEARCH_HOST:-http://elasticsearch:9200}"

echo "Waiting for Elasticsearch at ${ES_HOST}..."

max_attempts=20
attempt_num=1

until curl -s ${ES_HOST} > /dev/null; do
  if [ ${attempt_num} -ge ${max_attempts} ]; then
    echo "Elasticsearch is still not available after ${attempt_num} attempts. Exiting."
    exit 1
  fi
  echo "Elasticsearch is unavailable - sleeping (attempt: ${attempt_num}/${max_attempts})..."
  attempt_num=$((attempt_num+1))
  sleep 5
done

echo "Elasticsearch is up - starting search-service."

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
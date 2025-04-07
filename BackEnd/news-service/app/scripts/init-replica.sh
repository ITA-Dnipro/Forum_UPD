#!/bin/bash
set -e

MONGO_ROOT_USERNAME="${MONGO_INITDB_ROOT_USERNAME:-cool_user}"
MONGO_ROOT_PASSWORD="${MONGO_INITDB_ROOT_PASSWORD:-cool_password}"

echo "Waiting for MongoDB to be available..."
until mongo --host mongodb --username ${MONGO_INITDB_ROOT_USERNAME} --password ${MONGO_INITDB_ROOT_PASSWORD} --authenticationDatabase admin --quiet --eval "db.adminCommand('ping')" 2>/dev/null; do
    echo "MongoDB is not available yet, retrying in 2 seconds..."
    sleep 2
done

echo "Checking replica set status..."
STATUS=$(mongo --host mongodb --username ${MONGO_INITDB_ROOT_USERNAME} --password ${MONGO_INITDB_ROOT_PASSWORD} --authenticationDatabase admin --quiet --eval "rs.status().ok" 2>/dev/null || echo "0")
if [ "$STATUS" -eq "1" ]; then
   echo "Replica set already initiated."
else
   echo "Initiating replica set..."
   mongo --host mongodb --username ${MONGO_INITDB_ROOT_USERNAME} --password ${MONGO_INITDB_ROOT_PASSWORD} --authenticationDatabase admin --eval "rs.initiate({_id: 'rs0', members: [{ _id: 0, host: 'mongodb:27017' }]})"
fi

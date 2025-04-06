#!/bin/sh

# Apply migrations
python manage.py makemigrations
python manage.py migrate

# Start Kafka consumer in the background
python manage.py consume_roles &

python manage.py runserver 0.0.0.0:8000

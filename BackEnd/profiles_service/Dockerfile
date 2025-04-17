FROM python:3.9-alpine

WORKDIR /app

COPY . .

ENV PYTHONPATH=/app

RUN pip install --upgrade pip setuptools wheel && \
    apk add --no-cache g++ librdkafka-dev && \
    pip install -r requirements.txt

CMD ["python", "main.py" ]
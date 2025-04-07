FROM python:3.11

RUN apt-get update && apt-get install -y \
    wget unzip curl \
    chromium chromium-driver \
    && apt-get clean

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["celery", "-A", "utils_validation.celery.celery", "worker", "--loglevel=info"]
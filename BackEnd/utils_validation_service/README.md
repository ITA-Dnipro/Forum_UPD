# To run Utils & validation service:
# 1. Setup Enviroment variables
# .env
```
REDIS_URL=
REDIS_HOSTS=

RABBITMQ_URL=
RABBITMQ_USER=
RABBITMQ_PASSWORD=
```
# 2. To build and run microservice release version. Execute:
```shell
docker-compose -f docker-compose.utils.yml up --build
```
# To build and run microservice release version with dev tools. Execute:
```shell
docker-compose -f docker-compose.utils.yml -f docker-compose.utils_dev.yml up --build
```

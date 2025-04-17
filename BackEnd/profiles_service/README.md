### Required to install
* Python 3.9
* PostgreSQL 14

### To install all dependencies
```shell
$ pip install -r requirements.txt
```

### How to run in Docker

- Setup Docker  
> Setup .env
``` shell

SECRET_KEY= key ... # Use rules for hashed data
PROFILES_DB_NAME= Database name
PROFILES_DB_USER= Database user
PROFILES_DB_PASSWORD= Database user password
PROFILES_DB_HOST=sample filling => profiles_db(db container name) # Database host
PROFILES_DB_PORT=sample filling => 5432 # Database port
REDIS_URL=sample filling => "redis://redis_container:6379/0"
```


> Run Docker comands
```shell
$ docker docker-compose.profiles.yaml build
$ docker docker-compose.profiles.yaml up
$ docker exec -it profiles_service alembic upgrade head
```

> Stop Docker comands
```shell
ctrl + c
$ docker stop $(docker ps -q)
```

> To make migrations:
```shell
$ docker exec -it profiles_service alembic revision --autogenerate
```

FROM python:3.9-alpine

RUN addgroup -S forum && adduser -S forum -G forum

ENV HOME=/home/forum
ENV APP_HOME=$HOME/app

WORKDIR $APP_HOME

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk add --no-cache postgresql-dev gcc python3-dev musl-dev

COPY ./requirements.txt .

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . $APP_HOME

RUN chown -R forum:forum $APP_HOME

USER forum
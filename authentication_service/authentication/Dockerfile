FROM python:3.9-alpine

RUN addgroup -S authentication && adduser -S authentication -G authentication

ENV HOME=/home/authentication
ENV APP_HOME=$HOME/app

WORKDIR $APP_HOME

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apk add --no-cache gcc python3-dev musl-dev

COPY ./requirements.txt .

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . $APP_HOME

RUN chown -R authentication:authentication $APP_HOME

USER authentication

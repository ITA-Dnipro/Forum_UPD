FROM python:3.9-alpine

RUN addgroup -S authentication && adduser -S authentication -G authentication

ENV HOME=/home/authentication
ENV APP_HOME=$HOME/app

WORKDIR $APP_HOME

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY ./requirements.txt .

# Install necessary libraries and runtime dependencies
RUN apk add --no-cache \
    bash \
    libstdc++ \
    openssl-dev \
    libffi-dev \
    librdkafka \
    && apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    libc-dev \
    python3-dev \
    librdkafka-dev \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del .build-deps \
    && rm -rf /var/cache/apk/*


COPY . $APP_HOME/

RUN chown -R authentication:authentication $APP_HOME

USER authentication

ENV PATH="$HOME/.local/bin:$PATH"

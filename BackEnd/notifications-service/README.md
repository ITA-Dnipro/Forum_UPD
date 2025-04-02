# Kafka Consumer & Producer in Scala

## Overview

> This project implements a Kafka Consumer and Producer using Scala. The application interacts with Apache Kafka to publish and consume messages efficiently.

## Features

> Kafka Producer: Publishes messages to a specified Kafka topic.

> Kafka Consumer: Listens to messages from a Kafka topic and processes them.

> SmtpEmailSender: Manages sending email using SMTP

> Scalability: Supports multiple consumers and producers.

> Asynchronous Processing: Uses Kafka's event-driven architecture for high performance.

# Prerequisites

## Before running the application, ensure you have:

> docker

## Configuration (.env variables)

> EMAIL_HOST='smtp.gmail.com'

> EMAIL_PORT="587"

> EMAIL_USE_TLS=1

> EMAIL_HOST_USER=""

> EMAIL_HOST_PASSWORD=""

> KAFKA_BROKER="kafka:9092"

> EMAIL_TEMPLATES_PATH="src/main/scala/com/softserve/email_templates"

# Running the Application
## Start Kafka using Docker Compose:

> docker-composed up -d

# Troubleshooting

> Ensure Kafka is running before starting the consumer/producer. (kafka image)

> Check Kafka logs if messages are not being published or consumed. (scala-mail-service)

> Verify the topic name in constants. (Main.scala)

# Contributions
> Feel free to open issues and submit pull requests to improve the project.
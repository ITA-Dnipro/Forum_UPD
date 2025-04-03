package com.softserve.producers

import zio._
import zio.kafka.producer._
import zio.kafka.serde.Serde
import com.softserve.serde._
import zio.kafka.producer.{Producer, ProducerSettings}
import com.softserve.models._

object AuthMessageProducer {
  def produce(bootstrapServers: List[String], topic: String, message: AuthMessage): ZIO[Any, Throwable, Unit] = {
  val producerSettings = ProducerSettings(bootstrapServers)
    .withProperty("acks", "all")
    .withProperty("retries", "5")
    .withProperty("enable.idempotence", "true")
    .withProperty("request.timeout.ms", "5000")

    val retryStrategy = Schedule.exponential(500.milliseconds)  >>> Schedule.recurs(5)

    ZIO.scoped {
      for {
        producer <- Producer.make(producerSettings)
        .mapError(e => new RuntimeException("Failed to create Kafka producer", e))
        _ <- producer.produce(
          topic,
          message.email,  
          message,       
          Serde.string,
          AuthMessageSerde.serde
          ).retry(retryStrategy)
      } yield ()
    }.mapError { e =>
      Console.printLine(s"Error producing message to Kafka: ${e.getMessage}")
      e
    }
  }
}

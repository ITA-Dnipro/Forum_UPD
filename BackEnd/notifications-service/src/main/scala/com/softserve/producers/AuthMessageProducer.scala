package com.softserve.producers

import zio._
import zio.kafka.producer._
import zio.kafka.serde.Serde
import com.softserve.serde._
import zio.kafka.producer.{Producer, ProducerSettings}
import com.softserve.models._

import zio._
import zio.kafka.producer._
import zio.kafka.serde._
import zio.Schedule

object MessageProducer {

  def produce[K, V](
    bootstrapServers: List[String],
    topic: String,
    key: K,
    message: V,
    keySerde: Serde[Any, K],
    valueSerde: Serde[Any, V]
  ): ZIO[Any, Throwable, Unit] = {
    
    val producerSettings = ProducerSettings(bootstrapServers)
      .withProperty("acks", "all")
      .withProperty("retries", "5")
      .withProperty("enable.idempotence", "true")
      .withProperty("request.timeout.ms", "5000")

    val retryStrategy = Schedule.exponential(500.milliseconds) >>> Schedule.recurs(5)

    val scopedProduce = ZIO.scoped {
      for {
        producer <- Producer.make(producerSettings)
          .mapError(e => new RuntimeException("Failed to create Kafka producer", e))

        _ <- producer.produce(
          topic,
          key,
          message,
          keySerde,
          valueSerde
        )
      } yield ()
    }
    .catchAll { err =>
      Console.printLine(s"Error producing message to Kafka: ${err.getMessage}") *> ZIO.unit
    }
    scopedProduce.retry(retryStrategy)
  }
}
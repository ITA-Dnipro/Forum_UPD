package com.softserve.producers

import zio._
import zio.kafka.producer._
import zio.kafka.serde.Serde
import com.softserve.serde._
import zio.kafka.producer.{Producer, ProducerSettings}
import com.softserve.models._

object AuthMessageProducer {
  def produce(bootstrapServers: List[String], topic: String, message: AuthMessage): ZIO[Any, Throwable, Unit] = {

    ZIO.scoped {
      for {
        producer <- Producer.make(ProducerSettings(bootstrapServers))
        _ <- producer.produce(
          topic,
          message.email,  
          message,       
          Serde.string,
          AuthMessageSerde.serde
        )
        _ <- Console.printLine(s"CREATED REQUEST")
      } yield ()
    }
  }
}

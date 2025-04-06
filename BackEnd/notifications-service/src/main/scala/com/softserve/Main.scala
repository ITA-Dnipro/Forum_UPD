package com.softserve

import zio._
import org.apache.kafka.clients.producer.ProducerRecord
import zio.json._
import zio.kafka.consumer._
import zio.kafka.producer.{Producer, ProducerSettings}
import zio.kafka.serde._
import zio.stream.ZStream
import com.softserve.serde._
import org.fusesource.scalate.TemplateEngine
import com.softserve.helpers._  
import com.softserve.constants._  
import com.softserve.consumers._
import com.softserve.producers._
import com.softserve.models._
import com.softserve.serde._
import com.softserve.constants.EmailConstants._
object Main extends ZIOAppDefault {
  val bootstrapServers = sys.env.getOrElse("KAFKA_BROKER", "kafka:9092").split(",").toList
  val templateEngine = new TemplateEngine()
  val topic = TopicConstants.AUTHENTICATION

  override def run: ZIO[Any, Throwable, Unit] = 
      ZIO.scoped {(for {
      _ <- useEmailFields.provideLayer(emailConfigLayer)
      _ <- AuthMessageConsumer.run(bootstrapServers, templateEngine)
    } yield ()).tapError(err => ZIO.debug(s"Error: ${err.getMessage}"))
}
}

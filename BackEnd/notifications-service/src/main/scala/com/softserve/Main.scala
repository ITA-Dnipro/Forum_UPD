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

object Main extends ZIOAppDefault {
  val bootstrapServers = List("kafka:9092")
  val templateEngine = new TemplateEngine()
  val topic = TopicConstants.Authentication

  override def run: ZIO[Any, Throwable, Unit] = {
    try {
     
    for {
      // in need to produce
      // _ <- AuthMessageProducer.produce(bootstrapServers, topic, message)
      _ <- AuthMessageConsumer.run(bootstrapServers, templateEngine)

    } yield ()
  }
  catch {
      case ex: Exception => Console.printLine(s"${ex.getMessage}")
    } 
}
}

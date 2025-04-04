package com.softserve.consumers

import zio._
import zio.kafka.consumer._
import zio.kafka.serde.Serde
import java.io.File
import com.softserve.serde._
import com.softserve.constants._
import org.fusesource.scalate.TemplateEngine
import com.softserve.models._
import com.softserve.helpers._
import java.time.LocalDateTime

object AuthMessageConsumer {
  def run(bootstrapServers: List[String], templateEngine: TemplateEngine): ZIO[Any, Throwable, Unit] = {
    ZIO.scoped {
      for {
        consumer <- Consumer.make(
          ConsumerSettings(bootstrapServers).withGroupId("notifications-app")
          .withProperty("auto.offset.reset", "earliest")
        )
        _ <- consumer
          .plainStream(Subscription.topics(TopicConstants.AUTHENTICATION), Serde.string, AuthMessageSerde.serde)
          .tap { r =>
            val authMessage: AuthMessage = r.value
            ZIO.succeed {
              val validationErrors = authMessage.validate
              if (validationErrors.nonEmpty) {
                ZIO.debug(s"Validation failed: ${validationErrors.mkString(", ")}")
              } else {
                val sourceDataPath = new File(s"${EmailConstants.EmailTemplates.TEMPLATES_PATH}/${EmailConstants.EmailTemplates.CONFIRM_NAME}").getCanonicalPath
                val someAttributes = Map("name" -> authMessage.name, "link" -> authMessage.activationLink)
                val temp = templateEngine.layout(sourceDataPath, someAttributes).toString()
                for {
                _ <- SmtpEmailSender.sendEmail(
                  List(authMessage.email),
                  EmailConstants.CONFIRM_EMAIL_SUBJECT,
                  temp
                ).provideLayer(EmailConstants.emailConfigLayer)
              } yield ()
              }
            }.flatten
          }
          .map(_.offset)
          .aggregateAsync(Consumer.offsetBatches)
          .mapZIO(_.commit)
          .runDrain 
      } yield ()
    }
  }
}

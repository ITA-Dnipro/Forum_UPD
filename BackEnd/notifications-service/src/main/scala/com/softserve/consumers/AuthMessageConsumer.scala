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
        )
        _ <- consumer
          .plainStream(Subscription.topics(TopicConstants.AUTHENTICATION), Serde.string, AuthMessageSerde.serde)
          .tap { r =>
            val authMessage: AuthMessage = r.value
            val validationErrors = authMessage.validate
            if (validationErrors.nonEmpty) {
              Console.printLine(s"Validation failed: ${validationErrors.mkString(", ")}")
            } else {
            val email = authMessage.email
            val link = authMessage.activationLink
            val name = authMessage.name
            val sourceDataPath = new File(s"${EmailConstants.EmailTemplates.TEMPLATES_PATH}/${EmailConstants.EmailTemplates.CONFIRM_NAME}").getCanonicalPath
            val someAttributes = Map("name" -> name, "link" -> link)
            val temp = templateEngine.layout(sourceDataPath, someAttributes).toString()
            SmtpEmailSender.sendEmail(
              List(email),
              EmailConstants.CONFIRM_EMAIL_SUBJECT,
              temp)
              val endTime = LocalDateTime.now()
            }
          }
          .map(_.offset)
          .aggregateAsync(Consumer.offsetBatches)
          .mapZIO(_.commit)
          .runDrain 
      } yield ()
    }
  }
}

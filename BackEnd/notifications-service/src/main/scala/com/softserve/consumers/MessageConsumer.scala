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
import zio.stream.ZStream
import zio.Console.printLine
import zio.json.DecoderOps
import zio.json._

object MessageConsumer {

  def run(
    bootstrapServers: List[String],
    templateEngine: TemplateEngine
  ): ZIO[Any, Throwable, Unit] = {
    ZIO.scoped {
      for {
        consumer <- Consumer.make(
          ConsumerSettings(bootstrapServers)
            .withGroupId("notifications-app")
            .withProperty("auto.offset.reset", "earliest")
        )
        _ <- consumer
          .partitionedStream(Subscription.topics(TopicConstants.AUTHENTICATION, TopicConstants.PROFILE_IMAGE), Serde.string, Serde.string)
          .flatMapPar(Int.MaxValue) { case (topicPartition, partitionStream) =>
            ZStream.fromZIO(
              printLine(s"Starting stream for topic '${topicPartition.topic}' partition ${topicPartition.partition}")
            ) *>
              partitionStream
                .tap(record =>
                  processMessage(topicPartition.topic, record, templateEngine)
                )
                .map(_.offset)
          }
          .aggregateAsync(Consumer.offsetBatches)
          .mapZIO(_.commit)
          .runDrain
      } yield ()
    }
  }

  private def processMessage(
    topic: String,
    record: CommittableRecord[String, String],
    templateEngine: TemplateEngine
  ): ZIO[Any, Throwable, Unit] = {
    topic match {
      case TopicConstants.AUTHENTICATION =>
        process[AuthMessage](
          json = record.value,
          validate = _.validate,
          templateName = getAuthTemplateName,
          attributes = authAttributes,
          subject = EmailConstants.CONFIRM_EMAIL_SUBJECT,
          emailExtractor = a => List(a.email),
          templateEngine = templateEngine
        )

      case TopicConstants.PROFILE_IMAGE =>
        process[ProfileMessage](
          json = record.value,
          validate = _.validate,
          templateName = _ => EmailConstants.EmailTemplates.PROFILE,
          attributes = profileAttributes,
          subject = EmailConstants.PROFILE_EMAIL_SUBJECT,
          emailExtractor = p => List(p.email),
          templateEngine = templateEngine
        )

      case other =>
        printLine(s"[Unknown Topic: $other] key: ${record.key}, value: ${record.value}")
    }
  }

  private def process[T: JsonDecoder](
    json: String,
    validate: T => List[com.softserve.validations.ValidationUtils.ValidationError] ,
    templateName: T => String,
    attributes: T => Map[String, String],
    subject: String,
    emailExtractor: T => List[String],
    templateEngine: TemplateEngine
  ): ZIO[Any, Throwable, Unit] = {
    json.fromJson[T] match {
      case Left(error) =>
        printLine(s"[ERROR] Failed to parse JSON: $error")

      case Right(payload) =>
        val errors = validate(payload)
        if (errors.nonEmpty)
          ZIO.debug(s"Validation failed: ${errors.mkString(", ")}")
        else {
          val path = new File(s"${EmailConstants.EmailTemplates.TEMPLATES_PATH}/${templateName(payload)}").getCanonicalPath
          val emailBody = templateEngine.layout(path, attributes(payload)).toString()
          SmtpEmailSender.sendEmail(
            emailExtractor(payload),
            subject,
            emailBody
          ).provideLayer(EmailConstants.emailConfigLayer).unit
        }
    }
  }

  private def getAuthTemplateName(auth: AuthMessage): String =
    auth.message_type match {
      case "activation"     => EmailConstants.EmailTemplates.AUTH_CONFIRM
      case "password-reset" => EmailConstants.EmailTemplates.AUTH_RESET
      case other            => "unknown"
    }

  private def authAttributes(auth: AuthMessage): Map[String, String] =
    Map("name" -> auth.name, "link" -> auth.link)

  private def profileAttributes(p: ProfileMessage): Map[String, String] =
    Map(
      "email" -> p.email,
      "profile_name" -> p.profile_name,
      "updated_at" -> p.updated_at,
      "moderation_time" -> p.moderation_time,
      "image_path" -> p.image_path,
      "profile_view_url" -> p.profile_view_url
    )
}

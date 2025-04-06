package com.softserve.constants

import zio._

case class EmailConfig(
    EMAIL_HOST_USER: String,
    EMAIL_HOST: String,
    EMAIL_PORT: String,
    EMAIL_HOST_PASSWORD: String
)

object EmailConstants {
  final lazy val CONFIRM_EMAIL_SUBJECT: String = "Confirm your e-mail"
  final lazy val PROFILE_EMAIL_SUBJECT: String = "Підтвердження змін профілю"
  final lazy val MISSING_REQUIRED_ENV_VAR: String = "Missing required environment variable:"
  final lazy val EMAIL_SENT_SUCCESSFULLY_TO: String = "Email sent successfully to"
  final lazy val ERROR_SENDING_EMAIL: String = "Error sending email"
  final lazy val SMTP_AUTH_FAILED: String = "SMTP authentication failed"

  final lazy val emailConfig: Task[EmailConfig] = for {
    user <- ZIO.fromOption(sys.env.get("EMAIL_HOST_USER")).orElseFail(new RuntimeException(s"$MISSING_REQUIRED_ENV_VAR EMAIL_HOST_USER"))
    host <- ZIO.fromOption(sys.env.get("EMAIL_HOST"))orElseFail(new RuntimeException(s"$MISSING_REQUIRED_ENV_VAR EMAIL_HOST"))
    port <- ZIO.fromOption(sys.env.get("EMAIL_PORT"))orElseFail(new RuntimeException(s"$MISSING_REQUIRED_ENV_VAR EMAIL_PORT"))
    password <- ZIO.fromOption(sys.env.get("EMAIL_HOST_PASSWORD")).orElseFail(new RuntimeException(s"$MISSING_REQUIRED_ENV_VAR EMAIL_HOST_PASSWORD"))
    } yield EmailConfig(user, host, port, password)

  val emailConfigLayer: ZLayer[Any, Throwable, EmailConfig] = ZLayer.fromZIO(emailConfig)
  val useEmailFields: ZIO[EmailConfig, Throwable, Unit] = for {
    config <- ZIO.service[EmailConfig]
  } yield ()

  object EmailTemplates {
    final lazy val TEMPLATES_PATH: String = sys.env.getOrElse("EMAIL_TEMPLATES_PATH", "src/main/scala/com/softserve/email_templates") 
    final lazy val AUTH_CONFIRM: String = "ConfirmEmailTemplate.mustache"
    final lazy val EVENT_NAME: String = "EventActionTemplate.mustache"
    final lazy val AUTH_RESET: String = "ResetPasswordTemplate.mustache"
    final lazy val PROFILE: String = "ProfileImageChange.mustache"

  }
  }

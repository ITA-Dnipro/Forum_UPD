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
  final lazy val MISSING_REQUIRED_ENV_VAR: String = "Missing required environment variable:"
  final lazy val EMAIL_SENT_SUCCESSFULLY_TO: String = "Email sent successfully to"
  final lazy val ERROR_SENDING_EMAIL: String = "Error sending email"
  final lazy val SMTP_AUTH_FAILED: String = "SMTP authentication failed"
  val emailConfig: EmailConfig = EmailConfig(
    EMAIL_HOST_USER = sys.env.getOrElse("EMAIL_HOST_USER", throw new RuntimeException("Missing EMAIL_HOST_USER")),
    EMAIL_HOST = sys.env.getOrElse("EMAIL_HOST", throw new RuntimeException("Missing EMAIL_HOST")),
    EMAIL_PORT = sys.env.getOrElse("EMAIL_PORT", throw new RuntimeException("Missing EMAIL_PORT")),
    EMAIL_HOST_PASSWORD = sys.env.getOrElse("EMAIL_HOST_PASSWORD", throw new RuntimeException("Missing EMAIL_HOST_PASSWORD"))
  )
  object EmailTemplates {
    final lazy val TEMPLATES_PATH: String = sys.env.getOrElse("EMAIL_TEMPLATES_PATH", "src/main/scala/com/softserve/email_templates") 
    final lazy val CONFIRM_NAME: String = "ConfirmEmailTemplate.mustache"
    final lazy val EVENT_NAME: String = "EventActionTemplate.mustache"
    final lazy val RESET_PASSWORD_NAME: String = "ResetPasswordTemplate.mustache"
  }
  }   




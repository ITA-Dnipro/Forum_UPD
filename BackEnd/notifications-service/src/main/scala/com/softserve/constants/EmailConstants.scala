package com.softserve.constants

object EmailConstants {
  final val ConfirmEmailSubject: String = "Confirm your e-mail"
  final val MissingRequiredEnvVariable: String = "Missing required environment variable:"
  final val requiredEnvVars = Map(
    "EMAIL_HOST_USER" -> "Email host user",
    "EMAIL_HOST" -> "Email host",
    "EMAIL_PORT" -> "Email port",
    "EMAIL_HOST_PASSWORD" -> "Email host password"
    )
    final val envVars: Map[String, String] = requiredEnvVars.map { case (key, description) =>
      key -> sys.env.getOrElse(key, throw new RuntimeException(MissingRequiredEnvVariable + s"$key ($description)"))
    }
    final val EmailSentSuccessfulyTo: String = "Email sent successfully to"
    final val ErrorSendingEmail: String = "Error sending email"
    final val SMTPAuthFailed: String = "SMTP authentication failed"
    
  }   
  object EmailTemplates {
    final val TemplatesPath: String = "src/main/scala/com/softserve/email_templates"
    final val ConfirmName: String = "ConfirmEmailTemplate.mustache"
    final val EventName: String = "EventActionTemplate.mustache"
    final val ResetPasswordName: String = "ResetPasswordTemplate.mustache"
  }



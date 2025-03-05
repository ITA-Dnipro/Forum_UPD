package com.mycompany
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
}   


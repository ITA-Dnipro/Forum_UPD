package com.softserve.models

import zio._
import zio.json._
import com.softserve.validations._

case class AuthMessage(email: String, message_type: String, name: String, link: String) {
  def validate: List[ValidationUtils.ValidationError] = {
    val errors = ValidationUtils.validateEmail(email) ++
      ValidationUtils.validateString(message_type, "Message type") ++
      ValidationUtils.validateString(name, "Name") ++
      ValidationUtils.validateString(link, "Link")

    if (errors.nonEmpty) Unsafe.unsafe { implicit u =>
      Runtime.default.unsafe.run(ZIO.logError(s"Validation failed: ${errors.mkString(", ")}"))
    }
    errors
  }
}

object AuthMessage {
  implicit val encoder: JsonEncoder[AuthMessage] = DeriveJsonEncoder.gen[AuthMessage]
  implicit val decoder: JsonDecoder[AuthMessage] = DeriveJsonDecoder.gen[AuthMessage]

  val empty: AuthMessage = AuthMessage(
    email = "",
    message_type = "",
    name = "",
    link = ""
  )
}

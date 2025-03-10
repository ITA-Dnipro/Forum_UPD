package com.softserve.models

import com.softserve.validations.ValidationUtils
import zio.json._

case class AuthMessage(email: String, actionType: String, name: String, activationLink: String) {
  def validate: List[String] = {
    ValidationUtils.validateEmail(email) ++
    ValidationUtils.validateNonEmpty(actionType, "ActionType") ++
    ValidationUtils.validateNonEmpty(name, "Name") ++
    ValidationUtils.validateNonEmpty(activationLink, "ActivationLink")
  }
}

object AuthMessage {
  implicit val encoder: JsonEncoder[AuthMessage] = DeriveJsonEncoder.gen[AuthMessage]
  implicit val decoder: JsonDecoder[AuthMessage] = DeriveJsonDecoder.gen[AuthMessage]
}

package com.softserve.validations

object ValidationUtils {
  case class ValidationError(field: String, message: String)

  def validateEmail(email: String): List[ValidationError] = {
    val emailRegex = "^[A-Za-z0-9+_.-]+@(.+)$"
    validateString(email, "Email") ++
    List(
      Option.when(!email.matches(emailRegex))(ValidationError("Email", "Invalid format."))
    ).flatten
  }

  def validateString(field: String, fieldName: String): List[ValidationError] = {
    List(
      Option.when(field.isEmpty)(ValidationError(fieldName, s"Cannot be empty.")),
      Option.when(field.length > 255)(ValidationError(fieldName, s"Cannot be longer than 255 symbols."))
    ).flatten
  }
}

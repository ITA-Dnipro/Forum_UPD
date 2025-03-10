package com.softserve.validations

object ValidationUtils {

  def validateEmail(email: String): List[String] = {
    val emailRegex = "^[A-Za-z0-9+_.-]+@(.+)$"
    List(
      Option.when(email.isEmpty)("Email cannot be empty."),
      Option.when(!email.matches(emailRegex))("Invalid email format.")
    ).flatten
  }

  def validateNonEmpty(field: String, fieldName: String): List[String] = {
    Option.when(field.isEmpty)(s"$fieldName cannot be empty.").toList
  }
}

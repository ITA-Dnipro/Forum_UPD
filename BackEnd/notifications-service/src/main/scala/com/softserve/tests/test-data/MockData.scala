package com.softserve.testData
import com.softserve.models._

object MockData {
  final lazy val auth_activation_message = AuthMessage(
      email = "email.example@gmail.com",
      message_type = "activation",
      name = "User#1",
      link = "http://example.com"
  )
}
package com.softserve.testData
import com.softserve.models._

object MockData {
  final lazy val auth_message = AuthMessage(
      email = "email.example@gmail.com",
      actionType = "register",
      name = "User#1",
      activationLink = "http://example.com"
  )
}
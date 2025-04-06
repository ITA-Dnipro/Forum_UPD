package com.softserve.testData
import com.softserve.models._

object MockData {
  final lazy val auth_activation = AuthMessage(
      email = "email.example@gmail.com",
      message_type = "activation",
      name = "User#1",
      link = "http://example.com"
  )
  final lazy val auth_password_change = AuthMessage(
      email = "email.example@gmail.com",
      message_type = "password-reset",
      name = "User#1",
      link = "http://example.com"
  )
  final lazy val profile_image = ProfileMessage(
      email = "email.example@gmail.com",
      profile_name = "Mock Name",
      updated_at = "11.10.2003",
      moderation_time = "11.10.2003",
      image_path = "https://media.istockphoto.com/id/484234714/vector/example-free-grunge-retro-blue-isolated-stamp.jpg?s=612x612&w=0&k=20&c=97KgKGpcAKnn50Ubd8PawjUybzIesoXws7PdU_MJGzE=",
      profile_view_url = "http://example.com"
  )
}
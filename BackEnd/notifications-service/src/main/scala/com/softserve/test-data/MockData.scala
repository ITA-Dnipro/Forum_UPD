package com.softserve.testData
import com.softserve.models._

object MockData {
  final lazy val authActivation = AuthMessage(
      email = "email.example@gmail.com",
      message_type = "activation",
      name = "User#1",
      link = "http://example.com"
  )
  final lazy val authPasswordChange = AuthMessage(
      email = "email.example@gmail.com",
      message_type = "password-reset",
      name = "User#1",
      link = "http://example.com"
  )
  final lazy val profileImage = ProfileMessage(
      email = "email.example@gmail.com",
      profile_name = "Mock Name",
      updated_at = "2003-10-11",
      moderation_time = "2003-10-11",
      image_path = "https://media.istockphoto.com/id/484234714/vector/example-free-grunge-retro-blue-isolated-stamp.jpg?s=612x612&w=0&k=20&c=97KgKGpcAKnn50Ubd8PawjUybzIesoXws7PdU_MJGzE=",
      profile_view_url = "http://example.com"
  )
}
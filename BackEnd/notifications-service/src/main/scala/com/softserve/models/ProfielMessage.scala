package com.softserve.models

import zio._
import zio.json._
import com.softserve.validations._

case class ProfileMessage(
  email : String,
  profile_name : String,
  updated_at : String,
  moderation_time : String,
  image_path : String,
  profile_view_url : String
  ) {

  def validate: List[ValidationUtils.ValidationError] = {
    val errors = ValidationUtils.validateEmail(email) ++
      ValidationUtils.validateString(profile_name, "Profile name") ++
      ValidationUtils.validateString(updated_at, "Updated at") ++
      ValidationUtils.validateString(moderation_time, "Moderation time") ++
      ValidationUtils.validateString(image_path, "Image path") ++
      ValidationUtils.validateString(profile_view_url, "Profile view url")

    if (errors.nonEmpty) Unsafe.unsafe { implicit u =>
      Runtime.default.unsafe.run(ZIO.logError(s"Validation failed: ${errors.mkString(", ")}"))
    } 
    errors
  }
}

object ProfileMessage {
  implicit val encoder: JsonEncoder[ProfileMessage] = DeriveJsonEncoder.gen[ProfileMessage]
  implicit val decoder: JsonDecoder[ProfileMessage] = DeriveJsonDecoder.gen[ProfileMessage]

  val empty: ProfileMessage = ProfileMessage(
  email = "",
  profile_name = "",
  updated_at = "",
  moderation_time = "",
  image_path = "",
  profile_view_url = ""
  )

}

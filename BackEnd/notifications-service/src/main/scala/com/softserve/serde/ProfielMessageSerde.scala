package com.softserve.serde

import zio._
import zio.json._
import zio.kafka.serde.Serde
import com.softserve.models._

object ProfileMessageSerde {
  val serde: Serde[Any, ProfileMessage] =
    Serde.string.inmap(
      _.fromJson[ProfileMessage].getOrElse {
        println("Invalid Profile JSON, using fallback.")
        ProfileMessage.empty
      }
    )(_.toJson)
}
package com.softserve.serde

import zio._
import zio.json._
import zio.kafka.serde.Serde
import com.softserve.models._

object AuthMessageSerde {
  val serde: Serde[Any, AuthMessage] =
    Serde.string.inmap(
      _.fromJson[AuthMessage].getOrElse {
        println("Invalid AuthMessage JSON, using fallback.")
        AuthMessage.empty
      }
    )(_.toJson)
}
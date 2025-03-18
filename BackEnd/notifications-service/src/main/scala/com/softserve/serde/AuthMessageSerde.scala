package com.softserve.serde

import zio._
import zio.json._
import zio.kafka.serde.Serde
import com.softserve.models._

object AuthMessageSerde {
  val serde: Serde[Any, AuthMessage] =
    Serde.string.inmapZIO[Any, AuthMessage](
      s => ZIO.fromEither(s.fromJson[AuthMessage]).mapError(e => new RuntimeException(e))
    )(msg => ZIO.succeed(msg.toJson))
}

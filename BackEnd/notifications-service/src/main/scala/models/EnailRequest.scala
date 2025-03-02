package com.mycompany

import spray.json._

case class EmailRequest(email: String, link: String)

object EmailRequestJsonProtocol extends DefaultJsonProtocol {
  implicit val emailRequestFormat: RootJsonFormat[EmailRequest] = jsonFormat2(EmailRequest)
}

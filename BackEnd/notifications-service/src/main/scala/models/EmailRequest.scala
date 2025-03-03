package com.mycompany

import spray.json._

case class EmailRequest(email: String, link: String)

object EmailRequest {
  def apply(email: String, link: String): EmailRequest = {
    require(email.nonEmpty, "Email cannot be empty.")
    require(link.nonEmpty, "Link cannot be empty.")
    
    val emailRegex: String = "^[A-Za-z0-9+_.-]+@(.+)$"
    require(email.matches(emailRegex), "Invalid email format.")

    new EmailRequest(email, link) 
  }
}
object EmailRequestJsonProtocol extends DefaultJsonProtocol {

  implicit val emailRequestFormat: RootJsonFormat[EmailRequest] = jsonFormat2(EmailRequest)
}

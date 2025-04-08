package com.softserve.helpers

import zio._
import javax.mail._
import javax.mail.internet._
import com.softserve.constants._
import java.util.Properties

object SmtpEmailSender {
def sendEmail(receivers: Seq[String], subject: String, body: String): ZIO[EmailConfig, Throwable, String] = {
  for {
    config <- ZIO.service[EmailConfig]
    properties = new Properties()
    _ = properties.put("mail.smtp.host", config.EMAIL_HOST)
    _ = properties.put("mail.smtp.port", config.EMAIL_PORT)
    _ = properties.put("mail.smtp.auth", "true")
    _ = properties.put("mail.smtp.starttls.enable", "true")
    
    session = Session.getInstance(properties, new Authenticator {
      override def getPasswordAuthentication: PasswordAuthentication = 
        new PasswordAuthentication(config.EMAIL_HOST_USER, config.EMAIL_HOST_PASSWORD)
    })
    message = new MimeMessage(session)
    _ = message.setFrom(new InternetAddress(config.EMAIL_HOST_USER))
    _ <- ZIO.foreach(receivers) { recipient =>
      ZIO.attempt(message.addRecipient(Message.RecipientType.TO, new InternetAddress(recipient)))
    }
    _ = message.setSubject(subject, "UTF-8")
    _ = message.setContent(body, "text/html; charset=UTF-8")
    _ = message.setReplyTo(Array(new InternetAddress(config.EMAIL_HOST_USER)))
    
    result <- ZIO.attempt(Transport.send(message)) 
    _ = ZIO.debug("Email sent successfully") 
  } yield "Email sent successfully" 
}
}

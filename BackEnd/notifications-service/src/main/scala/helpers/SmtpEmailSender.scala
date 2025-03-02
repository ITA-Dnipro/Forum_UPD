package com.mycompany  
import org.slf4j.LoggerFactory
import java.util.Properties
import javax.mail.internet.{InternetAddress, MimeMessage}
import javax.mail._

object SmtpEmailSender {

  private val logger = LoggerFactory.getLogger("SmtpEmailSender")

  def sendEmail(
      receivers: Seq[String],
      subject: String, 
      body: String, 
      smtpHost: String, 
      smtpPort: String, 
      username: String, 
      password: String
  ): Either[String, String] = {

    val properties = new Properties()
    properties.put("mail.smtp.host", smtpHost)
    properties.put("mail.smtp.port", smtpPort)
    properties.put("mail.smtp.auth", "true")
    properties.put("mail.smtp.starttls.enable", "true") 

    val session = Session.getInstance(properties, new Authenticator {
      override def getPasswordAuthentication: PasswordAuthentication = 
        new PasswordAuthentication(username, password)
    })

    session.setDebug(false)

    try {
      val message = new MimeMessage(session)
      message.setFrom(new InternetAddress(username))
      
      receivers.foreach { recipient =>
        message.addRecipient(Message.RecipientType.TO, new InternetAddress(recipient))
      }

      message.setSubject(subject, "UTF-8")
      message.setContent(body, "text/html; charset=UTF-8")
      message.setReplyTo(Array(new InternetAddress(username)))

      Transport.send(message)
      logger.info(s"Email sent successfully to ${receivers.mkString(", ")}")
      Right(s"Email sent successfully to ${receivers.mkString(", ")}")
    } catch {
      case e: AuthenticationFailedException =>
        logger.error("SMTP authentication failed: ", e)
        Left("SMTP authentication failed. Check your username and password.")
      case e: MessagingException =>
        logger.error(s"Error sending email to ${receivers.mkString(", ")}: ", e)
        Left(s"Error sending email: ${e.getMessage}")
      case e: Exception =>
        logger.error("Unexpected error while sending email: ", e)
        Left(s"Unexpected error: ${e.getMessage}")
    }
  }
}
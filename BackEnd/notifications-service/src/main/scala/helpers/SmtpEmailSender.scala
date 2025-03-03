package com.mycompany  
import org.slf4j.LoggerFactory
import java.util.Properties
import javax.mail.internet.{InternetAddress, MimeMessage}
import javax.mail._

object SmtpEmailSender {

  private val logger = LoggerFactory.getLogger("SmtpEmailSender")

  val emailHost: String = EmailConstants.envVars("EMAIL_HOST")
  val emailPort: String = EmailConstants.envVars("EMAIL_PORT")
  val emailHostUser: String = EmailConstants.envVars("EMAIL_HOST_USER")
  val emailHostPassword: String = EmailConstants.envVars("EMAIL_HOST_PASSWORD")
  
  def sendEmail(
      receivers: Seq[String],
      subject: String, 
      body: String
  ): Either[String, String] = {

    val properties = new Properties()
    properties.put("mail.smtp.host", emailHost)
    properties.put("mail.smtp.port", emailPort)
    properties.put("mail.smtp.auth", "true")
    properties.put("mail.smtp.starttls.enable", "true") 

    val session = Session.getInstance(properties, new Authenticator {
      override def getPasswordAuthentication: PasswordAuthentication = 
        new PasswordAuthentication(emailHostUser, emailHostPassword)
    })

    session.setDebug(false)

    try {
      val message = new MimeMessage(session)
      message.setFrom(new InternetAddress(emailHostUser))
      
      receivers.foreach { recipient =>
        message.addRecipient(Message.RecipientType.TO, new InternetAddress(recipient))
      }

      message.setSubject(subject, "UTF-8")
      message.setContent(body, "text/html; charset=UTF-8")
      message.setReplyTo(Array(new InternetAddress(emailHostUser)))

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
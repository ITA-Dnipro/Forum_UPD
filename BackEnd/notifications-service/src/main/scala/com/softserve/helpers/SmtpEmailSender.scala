package com.softserve.helpers
import java.util.Properties
import javax.mail.internet.{InternetAddress, MimeMessage}
import javax.mail._
import com.softserve.constants._

object SmtpEmailSender {

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
      Right(EmailConstants.EmailSentSuccessfulyTo + s" ${receivers.mkString(", ")}")
    } catch {
      case e: AuthenticationFailedException =>
        Left(EmailConstants.SMTPAuthFailed)
      case e: MessagingException =>
        Left(EmailConstants.ErrorSendingEmail + s": ${e.getMessage}")
      case e: Exception =>
        Left(SystemConstants.UnexpectedError + s": ${e.getMessage}")
    }
  }
}
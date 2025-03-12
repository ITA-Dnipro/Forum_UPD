package com.softserve.helpers
import java.util.Properties
import javax.mail.internet.{InternetAddress, MimeMessage}
import javax.mail._
import com.softserve.constants._
val emailConfig = EmailConstants.emailConfig
object SmtpEmailSender {
  def sendEmail(
      receivers: Seq[String],
      subject: String, 
      body: String
  ): Either[String, String] = {

    val properties = new Properties()
    properties.put("mail.smtp.host", emailConfig.EMAIL_HOST)
    properties.put("mail.smtp.port", emailConfig.EMAIL_PORT)
    properties.put("mail.smtp.auth", "true")
    properties.put("mail.smtp.starttls.enable", "true") 
    val session = Session.getInstance(properties, new Authenticator {
    override def getPasswordAuthentication: PasswordAuthentication = 
      new PasswordAuthentication(emailConfig.EMAIL_HOST_USER, emailConfig.EMAIL_HOST_PASSWORD)
    })

    session.setDebug(false)

    try {
      val message = new MimeMessage(session)
      message.setFrom(new InternetAddress(emailConfig.EMAIL_HOST_USER))
      
      receivers.foreach { recipient =>
        message.addRecipient(Message.RecipientType.TO, new InternetAddress(recipient))
      }

      message.setSubject(subject, "UTF-8")
      message.setContent(body, "text/html; charset=UTF-8")
      message.setReplyTo(Array(new InternetAddress(emailConfig.EMAIL_HOST_USER)))

      Transport.send(message)
      Right(EmailConstants.EMAIL_SENT_SUCCESSFULLY_TO + s" ${receivers.mkString(", ")}")
    } catch {
      case e: AuthenticationFailedException =>
        Left(EmailConstants.SMTP_AUTH_FAILED)
      case e: MessagingException =>
        Left(EmailConstants.ERROR_SENDING_EMAIL + s": ${e.getMessage}")
      case e: Exception =>
        Left(SystemConstants.UNEXPECTED_ERROR + s": ${e.getMessage}")
    }
  }
}
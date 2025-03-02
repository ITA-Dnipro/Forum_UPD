package com.mycompany  
import akka.actor.ActorSystem 
import akka.http.scaladsl.Http 
import akka.http.scaladsl.server.Directives._ 
import akka.stream.ActorMaterializer  
import scala.concurrent.ExecutionContextExecutor  
import EmailRequestJsonProtocol._
import akka.http.scaladsl.model.StatusCodes
import akka.http.scaladsl.server.Route
import spray.json._
import akka.http.scaladsl.marshallers.sprayjson.SprayJsonSupport._
import org.fusesource.scalate.TemplateEngine

object Main extends App {   
	implicit val system: ActorSystem = ActorSystem("notifications-service")   
	implicit val materializer: ActorMaterializer = ActorMaterializer()   
	implicit val executionContext: ExecutionContextExecutor = system.dispatcher 
	val mainController = new MainController 
	val smtpEmailSender = SmtpEmailSender

	private val requiredEnvVars = Map(
		"EMAIL_HOST_USER" -> "Email host user",
		"EMAIL_HOST" -> "Email host",
		"EMAIL_PORT" -> "Email port",
		"EMAIL_HOST_PASSWORD" -> "Email host password"
	)

	private val envVars: Map[String, String] = requiredEnvVars.map { case (key, description) =>
		key -> sys.env.getOrElse(key, throw new RuntimeException(EmailConstants.MissingRequiredEnvVariable + s"$key ($description)"))
	}

	val emailHost: String = envVars("EMAIL_HOST")
	val emailPort: String = envVars("EMAIL_PORT")
	val emailHostUser: String = envVars("EMAIL_HOST_USER")
	val emailHostPassword: String = envVars("EMAIL_HOST_PASSWORD")
	val host: String =  sys.env.getOrElse("NOTIFICATIONS_HOST", "0.0.0.0")
	val port: Int = sys.env.get("NOTIFICATIONS_PORT").flatMap(_.toIntOption).getOrElse(8086)
	val templateEngine = new TemplateEngine

	val routes = List(
	path("hello") {
		get {
			complete(mainController.sayHello())
		}
	},
	path("auth" / "activate") {
		post {
			entity(as[EmailRequest]) { emailRequest =>
				val email = emailRequest.email
				val link = emailRequest.link
				val sourceDataPath = new java.io.File("src/main/scala/email_templates/emailTemplate.mustache").getCanonicalPath
				val someAttributes = Map("link" -> link)
				var temp = templateEngine.layout(sourceDataPath, someAttributes).toString()
				val responseMessage = smtpEmailSender.sendEmail(
					List(email), 
					EmailConstants.ConfirmEmailSubject, 
					temp, 
					emailHost, 
					emailPort, 
					emailHostUser, 
					emailHostPassword
				)
				complete(StatusCodes.OK, responseMessage)
			}
		}
	}
	)

	val route = routes.reduceLeft(_ ~ _) 

	Http().bindAndHandle(route, "0.0.0.0", port)
	println(s"Host: $host, Port: $port")
} 
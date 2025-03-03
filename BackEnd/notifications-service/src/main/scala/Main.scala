package com.mycompany  
import akka.actor.ActorSystem 
import akka.http.scaladsl.Http 
import akka.http.scaladsl.server.Directives._ 
import scala.concurrent.ExecutionContextExecutor  
import EmailRequestJsonProtocol._
import akka.http.scaladsl.model.StatusCodes
import akka.http.scaladsl.server.Route
import spray.json._
import akka.http.scaladsl.marshallers.sprayjson.SprayJsonSupport._
import org.fusesource.scalate.TemplateEngine

object Main extends App {   
	implicit val system: ActorSystem = ActorSystem("notifications-service")   
	implicit val executionContext: ExecutionContextExecutor = system.dispatcher 
	val mainController = new MainController 
	val smtpEmailSender = SmtpEmailSender
	val host: String =  sys.env.getOrElse("NOTIFICATIONS_HOST", "0.0.0.0")
	val port: Int = sys.env.get("NOTIFICATIONS_PORT") match {
	case Some(p) if p.forall(_.isDigit) => p.toInt
	case _ => 8086
	}
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
				val temp = templateEngine.layout(sourceDataPath, someAttributes).toString()
				val responseMessage = smtpEmailSender.sendEmail(
					List(email), 
					EmailConstants.ConfirmEmailSubject, 
					temp
				)
				complete(StatusCodes.OK, responseMessage)
			}
		}
	},
		path("health") {
		get {
			complete(StatusCodes.OK,"Notifications service is healthy")
		}
	},
	)

	val route = routes.reduceLeft(_ ~ _) 

	Http().bindAndHandle(route, host, port)
	println(s"Host: $host, Port: $port")
} 
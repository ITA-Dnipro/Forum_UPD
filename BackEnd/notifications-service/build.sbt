lazy val akkaHttpVersion = "10.7.0"
lazy val akkaVersion = "2.10.0"

resolvers += "Akka library repository".at("https://repo.akka.io/maven")
fork := true
lazy val root = (project in file("."))
  .settings(
        inThisBuild(List(
      organization    := "soft",
      scalaVersion    := "3.3.4",
    )),
    name := "notifications",
    libraryDependencies ++= Seq(
      "com.typesafe.akka" %% "akka-http"                % akkaHttpVersion,
      "com.typesafe.akka" %% "akka-http-spray-json"     % akkaHttpVersion,
      "com.typesafe.akka" %% "akka-actor-typed"         % akkaVersion,
      "com.typesafe.akka" %% "akka-stream"              % akkaVersion,
      "com.typesafe.akka" %% "akka-pki"                 % akkaVersion,
      "ch.qos.logback"    % "logback-classic"           % "1.2.11",
      "org.slf4j"         % "slf4j-api"                 % "1.7.36", 
      "com.sun.mail"      % "javax.mail"                % "1.6.2",
      "com.typesafe"      % "config"                    % "1.4.2",
      "ch.qos.logback"    % "logback-classic"           % "1.2.3",
      "org.scalatra.scalate" %% "scalate-core" % "1.10.1"
    )
  )

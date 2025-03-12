resolvers ++= Seq(
  "Confluent Maven Repository" at "https://packages.confluent.io/maven/",
  "Sonatype OSS Releases" at "https://oss.sonatype.org/content/repositories/releases/"
)
fork := true
lazy val root = (project in file("."))
  .settings(
        inThisBuild(List(
          organization    := "soft",
          scalaVersion    := "3.3.4",
    )),
    name := "notifications",
    libraryDependencies ++= Seq(
      "org.slf4j"               % "slf4j-nop"                 % "2.0.9",
      "com.sun.mail"            % "javax.mail"                % "1.6.2",
      "com.typesafe"            % "config"                    % "1.4.2",
      "org.scalatra.scalate"    %% "scalate-core"             % "1.10.1",
      "io.spray"                %% "spray-json"               % "1.3.6",
      "dev.zio"                 %% "zio"                      % "2.1.15",
      "dev.zio"                 %% "zio-streams"              % "2.1.15",
      "dev.zio"                 %% "zio-kafka"                % "2.10.0",
      "dev.zio"                 %% "zio-json"                 % "0.7.16"
    )
  )

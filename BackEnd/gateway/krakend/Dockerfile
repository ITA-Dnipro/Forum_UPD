FROM alpine/krakend:2.0
USER root
WORKDIR /etc/krakend

COPY *.json ./
COPY bash.sh ./bash.sh

RUN RUN chmod +x bash.sh


EXPOSE 8081
USER krakend
ENTRYPOINT ["./bash.sh"]

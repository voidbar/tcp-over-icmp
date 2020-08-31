FROM python:3-buster

RUN apt-get update && apt-get upgrade -y && update-ca-certificates
ADD src /src
WORKDIR /src

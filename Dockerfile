# syntax=docker/dockerfile:1

FROM golang:1.16-alpine

MAINTAINER John Allison "john123allison@gmail.com"

WORKDIR /app

COPY go.mod ./
COPY go.sum ./
RUN go mod download

COPY *.go ./
COPY config.json ./

RUN go build -o /hackpack-bot

CMD [ "/hackpack-bot" ]

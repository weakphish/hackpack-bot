# syntax=docker/dockerfile:1

FROM golang:1.23-rc-alpine3.19

WORKDIR /app

COPY go.mod ./
COPY go.sum ./
RUN go mod download

COPY *.go ./
COPY config.json ./

RUN go build -o /hackpack-bot

CMD [ "/hackpack-bot" ]

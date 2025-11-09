FROM golang:1.25.4 AS build-stage

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY ./main.go ./

RUN go build -o /go-backend

FROM alpine AS build-release-stage

WORKDIR /

COPY --from=build-stage /go-backend /go-backend

ENTRYPOINT ["/go-backend"]

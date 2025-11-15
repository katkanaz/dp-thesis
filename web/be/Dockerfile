FROM golang:1.25.4 AS build-stage

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY ./main.go ./

RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o /go-backend

FROM alpine AS build-release-stage

RUN apk add --no-cache ca-certificates

WORKDIR /

COPY --from=build-stage /go-backend /go-backend

ENTRYPOINT ["/go-backend"]

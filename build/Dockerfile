FROM golang:1.15 AS builder

WORKDIR /build

COPY . ./

ARG BUILD_VERSION=development
RUN CGO_ENABLED=0 go build -ldflags "-X vpnmon/internal/version.BuildVersion=$BUILD_VERSION" cmd/vpnmon/vpnmon.go

FROM alpine

WORKDIR /app

COPY --from=builder /build/vpnmon /app

EXPOSE 8080
ENTRYPOINT ["/app/vpnmon"]
CMD []

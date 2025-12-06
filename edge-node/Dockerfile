# Stage 1: Build
FROM golang:1.21-alpine AS builder
WORKDIR /app

# Copy file dependency
COPY go.mod go.sum ./
RUN go mod download

# Copy source code
COPY . .

# Build binary
RUN go build -o edge-app main.go

# Stage 2: Run
FROM alpine:latest
WORKDIR /app
COPY --from=builder /app/edge-app .

# Command jalan
CMD ["./edge-app"]
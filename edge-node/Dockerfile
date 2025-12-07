# Build stage
FROM golang:1.23-alpine AS builder

WORKDIR /app

# Install dependencies
RUN apk add --no-cache git

# Copy all source first
COPY . .

# Download dependencies and tidy
RUN go mod download && go mod tidy

# Build binary
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o edge-node .

# Runtime stage
FROM alpine:latest

RUN apk --no-cache add ca-certificates tzdata

WORKDIR /root/

# Copy binary from builder
COPY --from=builder /app/edge-node .

# Create non-root user
RUN addgroup -g 1000 appuser && \
    adduser -D -u 1000 -G appuser appuser && \
    chown -R appuser:appuser /root

USER appuser

EXPOSE 50051

CMD ["./edge-node"]
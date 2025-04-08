# Stage 1: Build
FROM golang:alpine AS builder

# Install dependencies
RUN apk update && apk add --no-cache git bash  # Added bash installation

# Set working directory
WORKDIR /build

# Copy source code
COPY . .

# Download Go dependencies and tidy up the modules
RUN go mod tidy
RUN go mod download

# Build the Go application
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -v -a -installsuffix cgo -o /go/bin/build ./cmd

# Stage 2: Final image
FROM alpine

# Install bash in the final image
RUN apk add --no-cache bash  # Added bash installation

# Copy the compiled binary and wait-for-it.sh from the builder stage
COPY --from=builder /go/bin/build /go/bin/build
COPY --from=builder /build/wait-for-it.sh ./wait-for-it.sh

# Make the wait-for-it script executable
RUN chmod +x wait-for-it.sh

# Set the entrypoint to use wait-for-it.sh
ENTRYPOINT ["/wait-for-it.sh", "postgres:5432", "--", "/go/bin/build"]

# Expose the application port
EXPOSE 8081

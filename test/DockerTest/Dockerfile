# Use an appropriate base image
FROM debian:latest

# Install OpenSSL
RUN apt-get update && apt-get install -y openssl

# Create directory for certificates
RUN mkdir /certs

# Generate the self-signed certificate and private key using a fixed hostname
RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /certs/selfsigned.key \
    -out /certs/selfsigned.crt \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=magnus-assistant"

# Expose any necessary ports (e.g., HTTPS 443)
EXPOSE 443

# Command to keep the container running
CMD ["tail", "-f", "/dev/null"]

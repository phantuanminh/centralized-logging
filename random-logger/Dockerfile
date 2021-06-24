FROM alpine:3.6

# Set working directory
WORKDIR /app

# Copy random-logging script to container
COPY ./entrypoint.sh /app/entrypoint.sh
ADD . /app

ENTRYPOINT ["sh", "/app/entrypoint.sh"]
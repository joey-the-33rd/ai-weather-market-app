#!/bin/bash

# Script to start the weather_db PostgreSQL database using Docker

# Configuration
CONTAINER_NAME="weather_db"
POSTGRES_USER="weather_user"
POSTGRES_PASSWORD="weather_password"
POSTGRES_DB="weather_data"
POSTGRES_PORT=5432

# Check if Docker is installed
if ! command -v docker &> /dev/null
then
    echo "Docker could not be found. Please install Docker or start PostgreSQL manually."
    exit 1
fi

# Check if container is already running
if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
    echo "Container $CONTAINER_NAME is already running."
else
    # Check if container exists but stopped
    if [ "$(docker ps -aq -f status=exited -f name=$CONTAINER_NAME)" ]; then
        echo "Starting existing container $CONTAINER_NAME..."
        docker start $CONTAINER_NAME
    else
        echo "Creating and starting new container $CONTAINER_NAME..."
        docker run -d \
            --name $CONTAINER_NAME \
            -e POSTGRES_USER=$POSTGRES_USER \
            -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD \
            -e POSTGRES_DB=$POSTGRES_DB \
            -p $POSTGRES_PORT:5432 \
            postgres:latest
    fi
fi

echo "✅ weather_db is running on port $POSTGRES_PORT."

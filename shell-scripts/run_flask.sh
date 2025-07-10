#!/bin/bash
# Run the Flask app_server.py with proper environment variable loading and port binding

# Load environment variables from .env file
export $(grep -v '^#' .env | xargs)

# Run the Flask app
python app_server.py

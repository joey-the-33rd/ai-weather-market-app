#!/bin/bash
# Safe test script for run_flask.sh without running Flask app

echo "Testing run_flask.sh script..."

# Check if .env file exists
if [ -f ".env" ]; then
  echo ".env file found."
else
  echo "Warning: .env file not found."
fi

# Check if app_server.py exists
if [ -f "app_server.py" ]; then
  echo "app_server.py found."
else
  echo "Warning: app_server.py not found."
fi

echo "run_flask.sh script test completed."

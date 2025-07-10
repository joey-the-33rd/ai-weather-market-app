#!/bin/bash
# Safe test script for run_app.sh without starting actual services

echo "Testing run_app.sh script..."

# Check if virtual environment directory exists
if [ -d ".venv" ]; then
  echo "Virtual environment found."
else
  echo "Warning: .venv directory not found. Skipping virtual environment activation."
fi

# Check if app_server.py exists
if [ -f "app_server.py" ]; then
  echo "app_server.py found."
else
  echo "Warning: app_server.py not found."
fi

# Check if WeatherApp directory exists
if [ -d "WeatherApp" ]; then
  echo "WeatherApp directory found."
else
  echo "Warning: WeatherApp directory not found."
fi

echo "run_app.sh script test completed."

#!/bin/bash
# Safe test script for run_ins_weather_data.sh without running the actual script

echo "Testing run_ins_weather_data.sh script..."

# Check if hardcoded virtual environment path exists
VENV_PATH="/Users/melchizedekvii/Documents/GitHub/ai-weather-market-app/ai-weather-market-app/aiwma_env/bin/activate"
if [ -f "$VENV_PATH" ]; then
  echo "Virtual environment activation script found at $VENV_PATH"
else
  echo "Warning: Virtual environment activation script not found at $VENV_PATH"
fi

# Check if ins-weather-data.py script exists
INS_SCRIPT="/Users/melchizedekvii/Documents/GitHub/ai-weather-market-app/ai-weather-market-app/ins-weather-data.py"
if [ -f "$INS_SCRIPT" ]; then
  echo "ins-weather-data.py script found at $INS_SCRIPT"
else
  echo "Warning: ins-weather-data.py script not found at $INS_SCRIPT"
fi

echo "run_ins_weather_data.sh script test completed."

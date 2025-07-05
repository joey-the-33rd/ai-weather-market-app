#!/bin/bash
# Script to activate the virtual environment and run the Flask app and React Native app

# Activate the virtual environment
source .venv/bin/activate

# Run the Flask app in the background
python app_server.py &

# Navigate to the React Native app directory and start the Metro bundler
cd WeatherApp
npm install
npm start

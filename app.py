import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv # type: ignore
import psycopg2 # type: ignore
import numpy as np
import joblib # type: ignore
import h2o # type: ignore
from h2o.estimators import H2OGradientBoostingEstimator # type: ignore
from flask import Flask, request, jsonify # type: ignore
from datetime import datetime, timedelta

load_dotenv()
app = Flask(__name__)

# Configure cache
CACHE_DURATION = timedelta(minutes=5)
prediction_cache = {}

# Load environment variables
API_KEY = os.getenv("WEATHER_API_KEY")
DB_PARAMS = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}

# Initialize H2O
h2o.init()
model_path = os.path.join(os.path.dirname(__file__), "h2o_automl_model", "GLM_1_AutoML_1_20250425_144833")
model = h2o.load_model(model_path)

# Define prediction endpoint using H2O model
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    # Convert input data to H2OFrame
    h2o_data = h2o.H2OFrame(data)
    # Make prediction
    prediction = model.predict(h2o_data)
    # Convert prediction to JSON serializable format
    pred_list = prediction.as_data_frame().values.flatten().tolist()
    return jsonify({'prediction': pred_list})

@app.route('/api/weather', methods=['GET'])
def get_weather():
    city = request.args.get('city')
    if not city:
        return jsonify({'error': 'City parameter is required'}), 400
    # Mock weather data for demonstration
    weather_data = {
        'temperature': 25,
        'humidity': 60,
        'weather': 'Sunny',
        'city': city
    }
    return jsonify(weather_data)

if __name__ == '__main__':
    app.run()

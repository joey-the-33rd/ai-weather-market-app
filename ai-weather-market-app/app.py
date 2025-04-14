from flask import Flask, request, jsonify # type: ignore
import requests # type: ignore
import os
from dotenv import load_dotenv # type: ignore
import psycopg2 # type: ignore
import numpy as np
import pandas as pd # type: ignore
from tensorflow.keras.models import load_model # type: ignore
from datetime import datetime, timedelta
from functools import lru_cache

load_dotenv()
app = Flask(__name__)

# Configure cache
CACHE_DURATION = timedelta(minutes=30)
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

# Load pre-trained LSTM model
MODEL_PATH = os.path.join("models", "lstm_weather_model.h5")
MODEL = load_model(MODEL_PATH)

@app.route("/weather", methods=["GET"])
def get_weather():
    """Get current weather data with caching and enhanced error handling"""
    city = request.args.get("city", "Nairobi").lower()
    cache_key = f"weather_{city}"

    # Check cache first
    if cache_key in prediction_cache and (datetime.now() - prediction_cache[cache_key]['timestamp']) < CACHE_DURATION:
        return jsonify(prediction_cache[cache_key]['data'])

    url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        weather = {
            "city": data["location"]["name"],
            "region": data["location"]["region"],
            "country": data["location"]["country"],
            "measurements": {
                "temperature_c": data["current"]["temp_c"],
                "humidity": data["current"]["humidity"],
                "wind_speed_kph": data["current"]["wind_kph"]
            },
            "conditions": {
                "text": data["current"]["condition"]["text"],
                "icon": data["current"]["condition"]["icon"]
            }
        }

        # Update cache
        prediction_cache[cache_key] = {
            'data': weather,
            'timestamp': datetime.now()
        }

        return jsonify(weather), 200, {'Cache-Control': 'public, max-age=1800'}

    except requests.exceptions.Timeout:
        return jsonify({
            "error": "Weather service timeout",
            "message": "The weather service did not respond in time",
            "suggestion": "Please try again later"
        }), 504
    except requests.exceptions.HTTPError as e:
        return jsonify({
            "error": "Weather service error",
            "status_code": e.response.status_code,
            "message": str(e),
            "documentation": "https://www.weatherapi.com/docs/"
        }), 502
    except Exception as e:
        return jsonify({
            "error": "Unexpected error",
            "type": e.__class__.__name__,
            "message": str(e),
            "support_contact": "support@weatherapp.com"
        }), 500

@app.route("/api/predict", methods=["GET"])
def predict_weather():
    """Predict weather parameters with enhanced input validation and multi-output support"""
    try:
        # Get prediction type from query params
        predict_type = request.args.get("type", "temperature").lower()
        valid_types = ["temperature", "humidity", "wind"]
        
        if predict_type not in valid_types:
            return jsonify({
                "error": "Invalid prediction type",
                "valid_types": valid_types
            }), 400

        # Check cache
        cache_key = f"predict_{predict_type}"
        if cache_key in prediction_cache and (datetime.now() - prediction_cache[cache_key]['timestamp']) < CACHE_DURATION:
            return jsonify(prediction_cache[cache_key]['data'])

        # Get historical data
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        
        if predict_type == "temperature":
            query = "SELECT temperature_c FROM weather_data ORDER BY recorded_at DESC LIMIT 10;"
        elif predict_type == "humidity":
            query = "SELECT humidity FROM weather_data ORDER BY recorded_at DESC LIMIT 10;"
        else:  # wind
            query = "SELECT wind_speed_kph FROM weather_data ORDER BY recorded_at DESC LIMIT 10;"

        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        conn.close()

        if len(records) < 10:
            return jsonify({
                "error": "Insufficient historical data",
                "required": 10,
                "available": len(records),
                "suggestion": "Try again later when more data is available"
            }), 400

        # Prepare input data
        input_data = np.array(records).reshape(1, 10, 1)
        
        # Make prediction (using same model for demo - in production would use specialized models)
        prediction = MODEL.predict(input_data)
        result = {
            "prediction": {
                "type": predict_type,
                "value": float(prediction[0][0]),
                "unit": "celsius" if predict_type == "temperature" else ("%" if predict_type == "humidity" else "kph")
            },
            "metadata": {
                "model": "LSTM",
                "input_size": 10,
                "timestamp": datetime.now().isoformat()
            }
        }

        # Update cache
        prediction_cache[cache_key] = {
            'data': result,
            'timestamp': datetime.now()
        }

        return jsonify(result), 200, {'Cache-Control': 'public, max-age=1800'}

    except psycopg2.Error as e:
        return jsonify({
            "error": "Database error",
            "type": e.__class__.__name__,
            "message": str(e),
            "support_contact": "dbsupport@weatherapp.com"
        }), 500
    except Exception as e:
        return jsonify({
            "error": "Prediction failed",
            "type": e.__class__.__name__,
            "message": str(e),
            "support_contact": "support@weatherapp.com"
        }), 500

@app.route("/api/predict/all", methods=["GET"])
def predict_all():
    """Predict all weather parameters at once"""
    try:
        # Check cache
        cache_key = "predict_all"
        if cache_key in prediction_cache and (datetime.now() - prediction_cache[cache_key]['timestamp']) < CACHE_DURATION:
            return jsonify(prediction_cache[cache_key]['data'])

        # Get all historical data
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT temperature_c, humidity, wind_speed_kph 
            FROM weather_data 
            ORDER BY recorded_at DESC 
            LIMIT 10;
        """)
        records = cursor.fetchall()
        cursor.close()
        conn.close()

        if len(records) < 10:
            return jsonify({
                "error": "Insufficient historical data",
                "required": 10,
                "available": len(records)
            }), 400

        # Prepare input data (using same model for demo)
        temp_data = np.array([r[0] for r in records]).reshape(1, 10, 1)
        humidity_data = np.array([r[1] for r in records]).reshape(1, 10, 1)
        wind_data = np.array([r[2] for r in records]).reshape(1, 10, 1)

        # Make predictions
        temp_pred = float(MODEL.predict(temp_data)[0][0])
        humidity_pred = float(MODEL.predict(humidity_data)[0][0])
        wind_pred = float(MODEL.predict(wind_data)[0][0])

        result = {
            "predictions": [
                {
                    "type": "temperature",
                    "value": temp_pred,
                    "unit": "celsius"
                },
                {
                    "type": "humidity",
                    "value": humidity_pred,
                    "unit": "%"
                },
                {
                    "type": "wind",
                    "value": wind_pred,
                    "unit": "kph"
                }
            ],
            "metadata": {
                "model": "LSTM",
                "input_size": 10,
                "timestamp": datetime.now().isoformat()
            }
        }

        # Update cache
        prediction_cache[cache_key] = {
            'data': result,
            'timestamp': datetime.now()
        }

        return jsonify(result), 200, {'Cache-Control': 'public, max-age=1800'}

    except Exception as e:
        return jsonify({
            "error": "Multi-prediction failed",
            "type": e.__class__.__name__,
            "message": str(e)
        }), 500

if __name__ == "__main__":
    app.run(debug=True)

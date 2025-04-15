from flask import Flask, request, jsonify # type: ignore
import requests # type: ignore
import os
from dotenv import load_dotenv # type: ignore
import psycopg2 # type: ignore
import numpy as np
import pandas as pd # type: ignore
import joblib # type: ignore
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

# Load pre-trained LSTM model and scaler
MODEL_PATH = os.path.join("models", "lstm_weather_model.h5")
SCALER_PATH = os.path.join("models", "scaler.save")
MODEL = load_model(MODEL_PATH)
SCALER = joblib.load(SCALER_PATH)

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
        
        # Update queries to fetch all 5 features used in training
        query = """
        SELECT temperature_c, humidity_percent, wind_speed_kmh, pressure_hpa, precipitation_mm
        FROM weather_data
        ORDER BY recorded_at DESC
        LIMIT 10;
        """

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

        # Prepare input data with all 5 features
        input_data = np.array(records).astype(np.float32)
        # Reshape to (seq_length, n_features)
        input_data = input_data.reshape(-1, input_data.shape[-1])
        # Scale input data
        input_data_scaled = SCALER.transform(input_data)
        # Create sequences
        seq_length = 10
        X_input = []
        for i in range(seq_length, len(input_data_scaled) + 1):
            X_input.append(input_data_scaled[i-seq_length:i])
        X_input = np.array(X_input)
        # Use the last sequence for prediction
        X_input = X_input[-1].reshape(1, seq_length, input_data.shape[1])

        # Make prediction
        prediction = MODEL.predict(X_input)
        # Map prediction output to feature index
        feature_map = {
            "temperature": 0,
            "humidity": 1,
            "wind": 2,
            "pressure": 3,
            "precipitation": 4
        }
        pred_index = feature_map.get(predict_type, 0)
        pred_value = float(prediction[0][pred_index]) if prediction.shape[1] > pred_index else None

        result = {
            "prediction": {
                "type": predict_type,
                "value": pred_value if pred_value is not None else "N/A",
                "unit": "celsius" if predict_type == "temperature" else ("%" if predict_type == "humidity" else ("kph" if predict_type == "wind" else ""))
            },
            "metadata": {
                "model": "LSTM",
                "input_size": seq_length,
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
            SELECT temperature_c, humidity_percent, wind_speed_kmh, pressure_hpa, precipitation_mm
            FROM weather_data 
            ORDER BY recorded_at DESC 
            LIMIT 10;
        """)
        records = cursor.fetchall()

        if len(records) < 10:
            cursor.close()
            conn.close()
            return jsonify({
                "error": "Insufficient historical data",
                "required": 10,
                "available": len(records)
            }), 400

        # Prepare input data (using same model for demo)
        # Update multi-predict endpoint to use all 5 features
        query = """
        SELECT temperature_c, humidity_percent, wind_speed_kmh, pressure_hpa, precipitation_mm
        FROM weather_data
        ORDER BY recorded_at DESC
        LIMIT 10;
        """
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        conn.close()

        if len(records) < 10:
            return jsonify({
                "error": "Insufficient historical data",
                "required": 10,
                "available": len(records)
            }), 400

        # Prepare input data with all 5 features
        combined_data = np.array(records).astype(np.float32)
        # Reshape and scale
        combined_data = combined_data.reshape(-1, combined_data.shape[-1])
        combined_data_scaled = SCALER.transform(combined_data)
        # Create sequences
        X_input = []
        for i in range(seq_length, len(combined_data_scaled) + 1):
            X_input.append(combined_data_scaled[i-seq_length:i])
        X_input = np.array(X_input)
        # Use last sequence for prediction
        X_input = X_input[-1].reshape(1, seq_length, combined_data.shape[1])

        # Make predictions
        preds = MODEL.predict(X_input)
        temp_pred = float(preds[0][0])
        humidity_pred = float(preds[0][1]) if preds.shape[1] > 1 else "N/A"
        wind_pred = float(preds[0][2]) if preds.shape[1] > 2 else "N/A"
        pressure_pred = float(preds[0][3]) if preds.shape[1] > 3 else "N/A"
        precipitation_pred = float(preds[0][4]) if preds.shape[1] > 4 else "N/A"

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
                },
                {
                    "type": "pressure",
                    "value": pressure_pred,
                    "unit": "hPa"
                },
                {
                    "type": "precipitation",
                    "value": precipitation_pred,
                    "unit": "mm"
                }
            ],
            "metadata": {
                "model": "LSTM",
                "input_size": seq_length,
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

@app.route("/", methods=["GET"])
def root():
    return {
        "message": "Welcome to the AI Weather & Market Prediction API",
        "endpoints": {
            "/weather": "Get current weather data. Query param: city (optional)",
            "/api/predict": "Predict weather parameter. Query param: type (temperature, humidity, wind)",
            "/api/predict/all": "Predict all weather parameters at once"
        }
    }

if __name__ == "__main__":
    app.run(debug=True)

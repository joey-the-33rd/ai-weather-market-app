from flask import Flask, request, jsonify # type: ignore
import requests # type: ignore
import os
from dotenv import load_dotenv # type: ignore
import psycopg2 # type: ignore
import numpy as np
import pandas as pd # type: ignore
from tensorflow.keras.models import load_model # type: ignore
from datetime import datetime

load_dotenv()
app = Flask(__name__)

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
MODEL = load_model("lstm_weather_model.h5")

@app.route("/weather", methods=["GET"])
def get_weather():
    city = request.args.get("city", "Nairobi")
    url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return jsonify({
            "city": data["location"]["name"],
            "region": data["location"]["region"],
            "country": data["location"]["country"],
            "temperature_c": data["current"]["temp_c"],
            "humidity": data["current"]["humidity"],
            "condition": data["current"]["condition"]["text"]
        })
    return jsonify({"error": "Could not fetch weather data"}), 400

@app.route("/api/predict", methods=["GET"])
def predict_weather():
    conn = psycopg2.connect(**DB_PARAMS)
    cursor = conn.cursor()
    cursor.execute("SELECT temperature_c FROM weather_data ORDER BY recorded_at DESC LIMIT 10;")
    records = cursor.fetchall()
    cursor.close()
    conn.close()

    if len(records) < 10:
        return jsonify({"error": "Not enough data to make a prediction."}), 400

    input_data = np.array(records).reshape(1, 10, 1)
    prediction = MODEL.predict(input_data)
    return jsonify({"predicted_temperature_c": float(prediction[0][0])})

if __name__ == "__main__":
    app.run(debug=True)

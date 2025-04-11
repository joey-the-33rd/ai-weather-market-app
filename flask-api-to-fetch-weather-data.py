from flask import Flask, request, jsonify  # type: ignore
import requests  # type: ignore
import json
import os
from datetime import datetime

app = Flask(__name__)

API_KEY = "7ee4289ca3374d4c88e51905250904"
MAX_CALLS_PER_MONTH = 999999
COUNTER_FILE = 'api_counter.json'


def load_counter():
    """Loads the API call counter from file."""
    if not os.path.exists(COUNTER_FILE):
        return {"count": 0, "month": datetime.now().month}
    with open(COUNTER_FILE, 'r') as f:
        return json.load(f)


def save_counter(counter):
    """Saves the API call counter to a file."""
    with open(COUNTER_FILE, 'w') as f:
        json.dump(counter, f)


@app.route('/weather', methods=['GET'])
def get_weather():
    """
    Handles GET requests to fetch current weather data for a specified city.
    Returns extended weather information in JSON format.
    """
    counter = load_counter()
    current_month = datetime.now().month

    # Reset count if it's a new month
    if counter["month"] != current_month:
        counter = {"count": 0, "month": current_month}

    if counter["count"] >= MAX_CALLS_PER_MONTH:
        return jsonify({"error": "Monthly request limit reached"}), 429

    city = request.args.get('city', 'Nairobi')
    url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}&aqi=no"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        weather = {
            "city": data["location"]["name"],
            "region": data["location"]["region"],
            "country": data["location"]["country"],
            "latitude": data["location"]["lat"],
            "longitude": data["location"]["lon"],
            "recorded_at": data["location"]["localtime"],
            "temperature_c": data["current"]["temp_c"],
            "humidity_percent": data["current"]["humidity"],
            "wind_speed_kmh": data["current"]["wind_kph"],
            "pressure_hpa": data["current"]["pressure_mb"],
            "precipitation_mm": data["current"]["precip_mm"],
            "weather_condition": data["current"]["condition"]["text"]
        }

        counter["count"] += 1
        save_counter(counter)
        return jsonify(weather)

    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Request failed", "details": str(e)}), 500
    except KeyError as e:
        return jsonify({"error": "Unexpected response structure", "missing_key": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)

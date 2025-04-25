import os
from datetime import datetime, timedelta
from dotenv import load_dotenv # type: ignore
from flask import Flask, request, jsonify # type: ignore
import requests # type: ignore
import json

# Load environment variables explicitly from the .env file in ai-weather-market-app directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), 'ai-weather-market-app', '.env'))

import h2o
from h2o.estimators.automl import H2OAutoML
import json

app = Flask(__name__)

# Initialize H2O and load the trained model at startup
h2o.init()
model_path = os.path.join(os.path.dirname(__file__), 'ai-weather-market-app', 'models', 'h2o_automl_model')
model = h2o.load_model(model_path)

@app.route('/', methods=['GET'])
def root():
    return jsonify({"status": "Flask app is running"}), 200

# Configure cache
CACHE_DURATION = timedelta(minutes=30)  # Cache weather data for 30 minutes
weather_cache = {}

# Configurations from .env
API_KEY = os.getenv("WEATHER_API_KEY")
MAX_CALLS_PER_MONTH = 999999
COUNTER_FILE = 'api_counter.json'

DB_PARAMS = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}

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
    city = request.args.get('city', 'Nairobi').lower()

    # Check cache first
    cache_key = f"current_{city}"
    if cache_key in weather_cache and (datetime.now() - weather_cache[cache_key]['timestamp']) < CACHE_DURATION:
        return jsonify(weather_cache[cache_key]['data'])

    # Reset count if it's a new month
    if counter["month"] != current_month:
        counter = {"count": 0, "month": current_month}

    if counter["count"] >= MAX_CALLS_PER_MONTH:
        return jsonify({
            "error": "Monthly request limit reached",
            "limit": MAX_CALLS_PER_MONTH,
            "current_count": counter["count"],
            "reset_time": f"Next month (month {current_month % 12 + 1})"
        }), 429

    url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}&aqi=no"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Validate response structure
        if not all(key in data for key in ['location', 'current']):
            raise ValueError("Invalid API response structure")

        weather = {
            "city": data["location"]["name"],
            "region": data["location"]["region"],
            "country": data["location"]["country"],
            "coordinates": {
                "latitude": data["location"]["lat"],
                "longitude": data["location"]["lon"]
            },
            "timestamp": data["location"]["localtime"],
            "measurements": {
                "temperature_c": data["current"]["temp_c"],
                "humidity_percent": data["current"]["humidity"],
                "wind_speed_kmh": data["current"]["wind_kph"],
                "pressure_hpa": data["current"]["pressure_mb"],
                "precipitation_mm": data["current"]["precip_mm"]
            },
            "conditions": {
                "text": data["current"]["condition"]["text"],
                "icon": data["current"]["condition"]["icon"]
            },
            "metadata": {
                "api_calls_this_month": counter["count"] + 1,
                "monthly_limit": MAX_CALLS_PER_MONTH
            }
        }

        # Update cache
        weather_cache[cache_key] = {
            'data': weather,
            'timestamp': datetime.now()
        }

        counter["count"] += 1
        save_counter(counter)
        return jsonify(weather), 200, {'Cache-Control': 'public, max-age=1800'}

    except requests.exceptions.Timeout:
        return jsonify({
            "error": "Service timeout",
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
    except (KeyError, ValueError) as e:
        return jsonify({
            "error": "Data processing error",
            "type": e.__class__.__name__,
            "message": str(e),
            "expected_format": "Standard WeatherAPI response structure"
        }), 500
    except Exception as e:
        return jsonify({
            "error": "Unexpected error",
            "type": e.__class__.__name__,
            "message": str(e),
            "support_contact": "support@weatherapp.com"
        }), 500


@app.route('/forecast', methods=['GET'])
def get_forecast():
    """Returns 3-day weather forecast for specified city"""
    city = request.args.get('city', 'Nairobi').lower()
    cache_key = f"forecast_{city}"

    # Check cache
    if cache_key in weather_cache and (datetime.now() - weather_cache[cache_key]['timestamp']) < CACHE_DURATION:
        return jsonify(weather_cache[cache_key]['data'])

    url = f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={city}&days=3&aqi=no"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        forecast = {
            "location": data["location"]["name"],
            "forecast": [
                {
                    "date": day["date"],
                    "day": {
                        "maxtemp_c": day["day"]["maxtemp_c"],
                        "mintemp_c": day["day"]["mintemp_c"],
                        "avgtemp_c": day["day"]["avgtemp_c"],
                        "condition": day["day"]["condition"]["text"],
                        "maxwind_kph": day["day"]["maxwind_kph"],
                        "totalprecip_mm": day["day"]["totalprecip_mm"]
                    }
                } for day in data["forecast"]["forecastday"]
            ]
        }

        # Update cache
        weather_cache[cache_key] = {
            'data': forecast,
            'timestamp': datetime.now()
        }

        return jsonify(forecast), 200, {'Cache-Control': 'public, max-age=1800'}

    except requests.exceptions.RequestException as e:
        return jsonify({
            "error": "Forecast request failed",
            "details": str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(debug=True, port=port)

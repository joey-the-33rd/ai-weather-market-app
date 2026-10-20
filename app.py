import os
from datetime import datetime, timedelta
from pathlib import Path

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

from weather_model import load_model_bundle, predict_next_hour, provider_hour_to_features

load_dotenv()
app = Flask(__name__)
CORS_ORIGINS = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "").split(",") if origin.strip()]
CORS(app, resources={r"/api/*": {"origins": CORS_ORIGINS}})

WEATHERAPI_KEY = os.getenv("WEATHERAPI_KEY")
WEATHERAPI_URL = "https://api.weatherapi.com/v1/forecast.json"
MODEL_PATH = os.getenv("WEATHER_MODEL_PATH", str(Path(__file__).resolve().parent / "weather_model.joblib"))
weather_model = None
try:
    if Path(MODEL_PATH).is_file():
        weather_model = load_model_bundle(MODEL_PATH)
        app.logger.info("Loaded weather forecasting model from %s", MODEL_PATH)
    else:
        app.logger.warning("Weather model artifact not found at %s; AI forecasts will return 503.", MODEL_PATH)
except Exception:
    app.logger.exception("Weather forecasting model could not be loaded")


def get_provider_forecast(location: str, days: int = 3):
    if not WEATHERAPI_KEY:
        return None, (jsonify({"error": "Weather service is not configured. Set WEATHERAPI_KEY on the server."}), 503)
    try:
        response = requests.get(
            WEATHERAPI_URL,
            params={"key": WEATHERAPI_KEY, "q": location, "days": days, "aqi": "yes", "alerts": "no"},
            timeout=(3.05, 12),
        )
        if response.status_code == 400:
            return None, (jsonify({"error": "Location was not recognized by the weather provider."}), 404)
        response.raise_for_status()
        return response.json(), None
    except requests.Timeout:
        return None, (jsonify({"error": "Weather provider timed out. Please try again."}), 504)
    except requests.RequestException:
        app.logger.exception("Weather provider request failed")
        return None, (jsonify({"error": "Weather data is temporarily unavailable."}), 502)
    except ValueError:
        app.logger.exception("Weather provider returned invalid JSON")
        return None, (jsonify({"error": "Weather provider returned an invalid response."}), 502)


@app.get("/")
def home():
    return jsonify({
        "name": "AI Weather Market App API",
        "status": "ok",
        "weather_endpoint": "/api/weather?location=Nairobi&mode=hourly",
        "ai_forecast_endpoint": "/api/ai-forecast?location=Nairobi&hours=24",
        "ai_model_loaded": weather_model is not None,
    })


@app.post("/login")
def login():
    return jsonify({
        "error": "Login is not configured. Configure a real user store or identity provider."
    }), 503


@app.post("/predict")
def legacy_predict():
    return jsonify({
        "error": "This legacy endpoint is retired. Use the dedicated AI weather forecast endpoint after training the weather model."
    }), 410


@app.get("/api/weather")
def get_weather():
    location = (request.args.get("location") or request.args.get("city") or "").strip()
    mode = (request.args.get("mode") or "hourly").lower()
    if not location:
        return jsonify({"error": "The location query parameter is required."}), 400
    if len(location) > 120:
        return jsonify({"error": "Location must be 120 characters or fewer."}), 400
    if mode not in {"hourly", "daily"}:
        return jsonify({"error": "mode must be 'hourly' or 'daily'."}), 400

    payload, error = get_provider_forecast(location)
    if error:
        return error
    location_data = payload.get("location", {})
    current = payload.get("current", {})
    forecast_days = payload.get("forecast", {}).get("forecastday", [])
    records = []

    if mode == "hourly":
        for day in forecast_days:
            for hour in day.get("hour", []):
                condition = hour.get("condition") or {}
                air_quality = hour.get("air_quality") or {}
                icon = condition.get("icon", "")
                records.append({
                    "city": location_data.get("name"), "country": location_data.get("country"),
                    "latitude": location_data.get("lat"), "longitude": location_data.get("lon"),
                    "recorded_at": hour.get("time"), "temperature_c": hour.get("temp_c"),
                    "humidity_percent": hour.get("humidity"), "pressure_hpa": hour.get("pressure_mb"),
                    "wind_speed_kmh": hour.get("wind_kph"), "wind_direction_deg": hour.get("wind_degree"),
                    "precipitation_mm": hour.get("precip_mm"), "uv_index": hour.get("uv"),
                    "air_quality_index": air_quality.get("us-epa-index"),
                    "weather_condition": condition.get("text"),
                    "weather_icon": "https:" + icon if icon else "",
                    "cloud_cover_percent": hour.get("cloud"), "visibility_km": hour.get("vis_km"),
                    "dew_point_c": hour.get("dewpoint_c"), "solar_radiation_w_m2": hour.get("short_rad"),
                })
    else:
        for day in forecast_days:
            day_data = day.get("day", {})
            condition = day_data.get("condition") or {}
            air_quality = current.get("air_quality") or {}
            icon = condition.get("icon", "")
            records.append({
                "city": location_data.get("name"), "country": location_data.get("country"),
                "latitude": location_data.get("lat"), "longitude": location_data.get("lon"),
                "recorded_at": day.get("date"), "temperature_c": day_data.get("avgtemp_c"),
                "humidity_percent": day_data.get("avghumidity"), "pressure_hpa": current.get("pressure_mb"),
                "wind_speed_kmh": day_data.get("maxwind_kph"), "wind_direction_deg": None,
                "precipitation_mm": day_data.get("totalprecip_mm"), "uv_index": day_data.get("uv"),
                "air_quality_index": air_quality.get("us-epa-index"),
                "weather_condition": condition.get("text"),
                "weather_icon": "https:" + icon if icon else "",
                "cloud_cover_percent": None, "visibility_km": None, "dew_point_c": None,
                "solar_radiation_w_m2": None,
            })
    return jsonify(records)


@app.get("/api/ai-forecast")
def get_ai_forecast():
    location = (request.args.get("location") or request.args.get("city") or "").strip()
    if not location:
        return jsonify({"error": "The location query parameter is required."}), 400
    if len(location) > 120:
        return jsonify({"error": "Location must be 120 characters or fewer."}), 400
    if weather_model is None:
        return jsonify({
            "error": "The AI weather model is not installed. Run python train_weather_model.py during deployment build, then restart the backend."
        }), 503
    try:
        hours_requested = int(request.args.get("hours", "24"))
    except ValueError:
        return jsonify({"error": "hours must be an integer from 1 to 48."}), 400
    if not 1 <= hours_requested <= 48:
        return jsonify({"error": "hours must be an integer from 1 to 48."}), 400

    payload, error = get_provider_forecast(location, days=3)
    if error:
        return error
    location_data = payload.get("location", {})
    latitude, longitude = location_data.get("lat"), location_data.get("lon")
    if latitude is None or longitude is None:
        return jsonify({"error": "The weather provider did not return location coordinates."}), 502

    try:
        local_time = datetime.strptime(location_data["localtime"], "%Y-%m-%d %H:%M")
        start_of_current_hour = local_time.replace(minute=0, second=0, microsecond=0)
        future_hours = []
        for day in payload.get("forecast", {}).get("forecastday", []):
            for hour in day.get("hour", []):
                stamp = datetime.strptime(hour["time"], "%Y-%m-%d %H:%M")
                if stamp >= start_of_current_hour:
                    future_hours.append((stamp, hour))
        future_hours.sort(key=lambda item: item[0])
        predictions = []
        for stamp, hour in future_hours[:hours_requested]:
            features = provider_hour_to_features(hour, float(latitude), float(longitude))
            prediction = predict_next_hour(weather_model, features)
            predictions.append({
                "input_time": stamp.strftime("%Y-%m-%d %H:%M"),
                "valid_at": (stamp + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M"),
                "temperature_c": prediction["temperature_c"],
                "precipitation_mm": prediction["precipitation_mm"],
            })
        if not predictions:
            return jsonify({"error": "The provider returned no hourly records for this forecast window."}), 502
    except (KeyError, TypeError, ValueError):
        app.logger.exception("Could not prepare features for AI forecast")
        return jsonify({"error": "Could not prepare weather features for the AI model."}), 502
    except Exception:
        app.logger.exception("AI forecast inference failed")
        return jsonify({"error": "AI prediction failed. Check the model artifact and feature schema."}), 500

    return jsonify({
        "location": {
            "name": location_data.get("name"), "country": location_data.get("country"),
            "latitude": latitude, "longitude": longitude,
        },
        "model": {
            "name": weather_model.get("model_name", "Weather forecasting model"),
            "version": weather_model.get("model_version", 1),
            "trained_from": weather_model.get("trained_from"),
            "trained_through": weather_model.get("trained_through"),
            "data_source": weather_model.get("data_source"),
        },
        "metrics": weather_model.get("metrics", {}),
        "forecasts": predictions,
        "note": "One-hour-ahead model estimates using the provider's hourly forecast as input. Holdout metrics do not guarantee future accuracy.",
    })


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5050"))
    app.run(host="0.0.0.0", port=port, debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")

import os
from functools import wraps

import h2o
import jwt
import requests
from dotenv import load_dotenv
from flask import Flask, abort, jsonify, request

load_dotenv()
app = Flask(__name__)

WEATHERAPI_KEY = os.getenv("WEATHERAPI_KEY")
JWT_SECRET = os.getenv("JWT_SECRET")
WEATHERAPI_URL = "https://api.weatherapi.com/v1/forecast.json"

# Model loading is optional for the weather API. A missing model must not
# prevent the weather endpoint from starting.
MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "models",
    "h2o_automl_model",
    "GLM_1_AutoML_1_20250425_144833",
)
model = None
if os.path.exists(MODEL_PATH):
    try:
        h2o.init()
        model = h2o.load_model(MODEL_PATH)
    except Exception:
        app.logger.exception("H2O initialization/model loading failed")
else:
    app.logger.warning("H2O model directory not found: %s", MODEL_PATH)


def require_jwt(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not JWT_SECRET:
            return jsonify({"error": "JWT authentication is not configured"}), 503
        auth_header = request.headers.get("Authorization", "")
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            abort(401, description="Missing or invalid Bearer token")
        try:
            jwt.decode(parts[1], JWT_SECRET, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            abort(401, description="Token has expired")
        except jwt.InvalidTokenError:
            abort(401, description="Invalid token")
        return func(*args, **kwargs)
    return wrapper


@app.get("/")
def home():
    return jsonify({
        "name": "AI Weather Market App API",
        "status": "ok",
        "weather_endpoint": "/api/weather?location=Nairobi&mode=hourly",
    })


@app.post("/login")
def login():
    # This repository does not yet have a real user store. Never issue JWTs
    # using hardcoded demo credentials; configure an identity provider first.
    return jsonify({
        "error": "Login is not configured. Configure a real user store or identity provider."
    }), 503


@app.post("/predict")
@require_jwt
def predict():
    if model is None:
        return jsonify({"error": "Prediction model is unavailable; check server model configuration."}), 503
    data = request.get_json(silent=True)
    if not isinstance(data, (dict, list)) or not data:
        return jsonify({"error": "Provide a JSON object or list of model features."}), 400
    try:
        prediction = model.predict(h2o.H2OFrame(data))
        values = prediction.as_data_frame().values.flatten().tolist()
        return jsonify({"prediction": values})
    except Exception:
        app.logger.exception("Prediction failed")
        return jsonify({"error": "Prediction failed. Check the supplied features and model schema."}), 400


@app.get("/api/weather")
def get_weather():
    # The web frontend calls this endpoint without a token, so weather lookup
    # is public while prediction endpoints remain authenticated.
    location = (request.args.get("location") or request.args.get("city") or "").strip()
    mode = (request.args.get("mode") or "hourly").lower()
    if not location:
        return jsonify({"error": "The location query parameter is required."}), 400
    if len(location) > 120:
        return jsonify({"error": "Location must be 120 characters or fewer."}), 400
    if mode not in {"hourly", "daily"}:
        return jsonify({"error": "mode must be 'hourly' or 'daily'."}), 400
    if not WEATHERAPI_KEY:
        return jsonify({"error": "Weather service is not configured. Set WEATHERAPI_KEY on the server."}), 503

    try:
        response = requests.get(
            WEATHERAPI_URL,
            params={"key": WEATHERAPI_KEY, "q": location, "days": 3, "aqi": "yes", "alerts": "no"},
            timeout=(3.05, 12),
        )
        if response.status_code == 400:
            return jsonify({"error": "Location was not recognized by the weather provider."}), 404
        response.raise_for_status()
        payload = response.json()
    except requests.Timeout:
        return jsonify({"error": "Weather provider timed out. Please try again."}), 504
    except requests.RequestException:
        app.logger.exception("Weather provider request failed")
        return jsonify({"error": "Weather data is temporarily unavailable."}), 502
    except ValueError:
        app.logger.exception("Weather provider returned invalid JSON")
        return jsonify({"error": "Weather provider returned an invalid response."}), 502

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
                    "city": location_data.get("name"),
                    "country": location_data.get("country"),
                    "latitude": location_data.get("lat"),
                    "longitude": location_data.get("lon"),
                    "recorded_at": hour.get("time"),
                    "temperature_c": hour.get("temp_c"),
                    "humidity_percent": hour.get("humidity"),
                    "pressure_hpa": hour.get("pressure_mb"),
                    "wind_speed_kmh": hour.get("wind_kph"),
                    "wind_direction_deg": hour.get("wind_degree"),
                    "precipitation_mm": hour.get("precip_mm"),
                    "uv_index": hour.get("uv"),
                    "air_quality_index": air_quality.get("us-epa-index"),
                    "weather_condition": condition.get("text"),
                    "weather_icon": "https:" + icon if icon else "",
                    "cloud_cover_percent": hour.get("cloud"),
                    "visibility_km": hour.get("vis_km"),
                    "dew_point_c": hour.get("dewpoint_c"),
                    "solar_radiation_w_m2": hour.get("short_rad"),
                })
    else:
        for day in forecast_days:
            day_data = day.get("day", {})
            condition = day_data.get("condition") or {}
            air_quality = current.get("air_quality") or {}
            icon = condition.get("icon", "")
            records.append({
                "city": location_data.get("name"),
                "country": location_data.get("country"),
                "latitude": location_data.get("lat"),
                "longitude": location_data.get("lon"),
                "recorded_at": day.get("date"),
                "temperature_c": day_data.get("avgtemp_c"),
                "humidity_percent": day_data.get("avghumidity"),
                "pressure_hpa": current.get("pressure_mb"),
                "wind_speed_kmh": day_data.get("maxwind_kph"),
                "wind_direction_deg": None,
                "precipitation_mm": day_data.get("totalprecip_mm"),
                "uv_index": day_data.get("uv"),
                "air_quality_index": air_quality.get("us-epa-index"),
                "weather_condition": condition.get("text"),
                "weather_icon": "https:" + icon if icon else "",
                "cloud_cover_percent": None,
                "visibility_km": None,
                "dew_point_c": None,
                "solar_radiation_w_m2": None,
            })

    return jsonify(records)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5050"))
    app.run(
        host="0.0.0.0",
        port=port,
        debug=os.getenv("FLASK_DEBUG", "false").lower() == "true",
    )

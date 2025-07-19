import os
from datetime import datetime, timedelta
from dotenv import load_dotenv # type: ignore
from flask import Flask, request, jsonify, abort # type: ignore
import requests # type: ignore
import json
import jwt  # type: ignore
from functools import wraps

# Load environment variables explicitly from the .env file in ai-weather-market-app directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

import h2o
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

JWT_SECRET = os.getenv("JWT_SECRET", "your_jwt_secret_key")

def require_jwt(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Debug: log all headers and environ keys
        print("📤 Request Headers:", request.headers)
        print("📤 Request Environ Keys:", request.environ.keys())
        auth_header = request.headers.get('Authorization', None)
        if not auth_header:
            auth_header = request.environ.get('HTTP_AUTHORIZATION', None)
        # print("Authorization header received:", auth_header)  # Debug log removed for production
        if not auth_header:
            abort(401, description="Unauthorized: Missing Authorization header")
        parts = auth_header.split()
        if parts[0].lower() != 'bearer' or len(parts) != 2:
            abort(401, description="❌ Unauthorized: Invalid Authorization header format")
        token = parts[1]
        # print("JWT token extracted:", token)  # Debug log removed for production
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            # print("Decoded JWT payload:", payload)  # Debug log removed for production
            # Optionally, you can add user info to request context here
        except jwt.ExpiredSignatureError:
            abort(401, description="ℹ️ Unauthorized: Token has expired")
        except jwt.InvalidTokenError as e:
            # print("JWT decode error:", str(e))  # Debug log removed for production
            abort(401, description="ℹ️ Unauthorized: Invalid token")
        return func(*args, **kwargs)
    return wrapper


@app.route('/')
def home():
    return "👋 Welcome to the AI Weather Market App API. Use the /predict endpoint to get weather predictions."

# Initialize H2O and load the trained model at startup
h2o.init()
model_path = os.path.join(os.path.dirname(__file__), 'models', 'h2o_automl_model', 'GLM_1_AutoML_1_20250425_144833')
model = h2o.load_model(model_path)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    # For demonstration, use a simple check. Replace with real user validation.
    if username == 'admin' and password == 'password':
        payload = {
            'sub': username,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=1)
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
        # Do not display token in response for production, return a success message instead
        return jsonify({'message': '✅ Login successful'})
    else:
        abort(401, description="❌ Unauthorized: Invalid credentials")

@app.route('/predict', methods=['POST'])
@require_jwt
def predict():
    """
    Accepts live weather data as JSON payload and returns AI model prediction.
    """
    try:
        input_data = request.get_json()
        if not input_data:
            return jsonify({"error": "No input data provided"}), 400

        # If input_data is a list, take the first element
        if isinstance(input_data, list):
            input_data = input_data[0]

        # Convert input JSON to H2OFrame with explicit column order and types
        # Define expected columns in the order the model expects
        expected_columns = [
            "humidity_percent",
            "wind_speed_kmh",
            "pressure_hpa",
            "precipitation_mm",
            "wind_direction_deg",
            "uv_index",
            "air_quality_index",
            "cloud_cover_percent",
            "visibility_km",
            "dew_point_c",
            "solar_radiation_w_m2",
            "weather_condition"
        ]

        # Create a list of dicts with all expected columns, filling missing with None
        row = {}
        for col in expected_columns:
            row[col] = input_data.get(col, None)

        # Validate that no required field is None except weather_condition which can be None
        for col in expected_columns:
            if col != "weather_condition" and row[col] is None:
                return jsonify({"error": f"Missing required field: {col}"}), 400

        import pandas as pd

        # Create pandas DataFrame with expected columns
        expected_columns = [
            "humidity_percent",
            "wind_speed_kmh",
            "pressure_hpa",
            "precipitation_mm",
            "wind_direction_deg",
            "uv_index",
            "air_quality_index",
            "cloud_cover_percent",
            "visibility_km",
            "dew_point_c",
            "solar_radiation_w_m2",
            "weather_condition"
        ]
        data_dict = {col: [input_data.get(col, None)] for col in expected_columns}

        # Set weather_condition as categorical with correct categories
        # Updated list of allowed weather_condition categories based on WeatherAPI.com
        allowed_weather_conditions = [
            "Sunny",
            "Clear",
            "Partly cloudy",
            "Cloudy",
            "Overcast",
            "Mist",
            "Patchy rain possible",
            "Patchy snow possible",
            "Patchy sleet possible",
            "Patchy freezing drizzle possible",
            "Thundery outbreaks possible",
            "Blowing snow",
            "Blizzard",
            "Fog",
            "Freezing fog",
            "Patchy light drizzle",
            "Light drizzle",
            "Freezing drizzle",
            "Heavy freezing drizzle",
            "Patchy light rain",
            "Light rain",
            "Moderate rain at times",
            "Moderate rain",
            "Heavy rain at times",
            "Heavy rain",
            "Light freezing rain",
            "Moderate or heavy freezing rain",
            "Light sleet",
            "Moderate or heavy sleet",
            "Patchy light snow",
            "Light snow",
            "Patchy moderate snow",
            "Moderate snow",
            "Patchy heavy snow",
            "Heavy snow",
            "Ice pellets",
            "Light rain shower",
            "Moderate or heavy rain shower",
            "Torrential rain shower",
            "Light sleet showers",
            "Moderate or heavy sleet showers",
            "Light snow showers",
            "Moderate or heavy snow showers",
            "Light showers of ice pellets",
            "Moderate or heavy showers of ice pellets",
            "Patchy light rain with thunder",
            "Moderate or heavy rain with thunder",
            "Patchy light snow with thunder",
            "Moderate or heavy snow with thunder"
        ]
        df = pd.DataFrame(data_dict)
        df['weather_condition'] = pd.Categorical(df['weather_condition'], categories=allowed_weather_conditions)

        # Convert pandas DataFrame to H2OFrame
        hf = h2o.H2OFrame(df)

        # Predict using the loaded model
        prediction = model.predict(hf)

        # Extract prediction result
        pred_value = prediction.as_data_frame().iloc[0, 0]

        return jsonify({"prediction": pred_value}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/weather', methods=['GET'])
@require_jwt
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
    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables from .env file
    import os
    port_str = os.getenv("PORT", "5050")
    try:
        port = int(port_str)
    except ValueError:
        port = 5050
    app.run(debug=True, host='0.0.0.0', port=port)

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv # type: ignore
from flask import Flask, request, jsonify # type: ignore
import requests # type: ignore
import json

# Load environment variables explicitly from the .env file in ai-weather-market-app directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

import h2o
import json

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to the AI Weather Market App API. Use the /predict endpoint to get weather predictions."

# Initialize H2O and load the trained model at startup
h2o.init()
model_path = os.path.join(os.path.dirname(__file__), 'models', 'h2o_automl_model', 'GLM_1_AutoML_1_20250425_144833')
model = h2o.load_model(model_path)

@app.route('/predict', methods=['POST'])
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

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(debug=True, port=port)

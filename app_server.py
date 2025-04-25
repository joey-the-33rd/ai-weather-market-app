import os
from datetime import datetime, timedelta
from dotenv import load_dotenv # type: ignore
from flask import Flask, request, jsonify # type: ignore
import requests # type: ignore
import json

# Load environment variables explicitly from the .env file in ai-weather-market-app directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), 'ai-weather-market-app', '.env'))

import h2o
import json

app = Flask(__name__)

# Initialize H2O and load the trained model at startup
h2o.init()
model_path = os.path.join(os.path.dirname(__file__), 'ai-weather-market-app', 'models', 'h2o_automl_model', 'GLM_1_AutoML_1_20250425_144833')
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
        weather_condition_domain = model._model_json['output']['domains'][-1]  # last column domain
        df = pd.DataFrame(data_dict)
        df['weather_condition'] = pd.Categorical(df['weather_condition'], categories=weather_condition_domain)

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

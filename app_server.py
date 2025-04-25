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

        # Convert input JSON to H2OFrame
        hf = h2o.H2OFrame([input_data])

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

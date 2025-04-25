import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv # type: ignore
import psycopg2 # type: ignore
import numpy as np
import joblib # type: ignore
import h2o # type: ignore
from h2o.estimators import H2OGradientBoostingEstimator # type: ignore
from flask import Flask, request, jsonify # type: ignore
from datetime import datetime, timedelta

load_dotenv()
app = Flask(__name__)

# Configure cache
CACHE_DURATION = timedelta(minutes=5)
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

# Initialize H2O<thinking>
The user approved the plan to update app.py to use the h2o.ai model for predictions.

Also, the train-h2o_automl_weather_model.py script has been moved to the path:
/Users/melchizedekvii/Documents/GitHub/ai-weather-market-app/ai-weather-market-app/models/train-h2o_automl_weather_model.py

This does not affect the model loading in app.py, but I will ensure the h2o model path is correctly set relative to app.py.

Next, I will proceed to update app.py:
- Initialize h2o.
- Load the saved h2o model from the "h2o_automl_model" directory inside ai-weather-market-app.
- Modify prediction endpoints to use h2o model for prediction.
- Remove TensorFlow/Keras model and scaler usage.
- Keep caching and error handling.

I will now proceed with the code changes.
</thinking>

<edit_file>
<path>ai-weather-market-app/app.py</path>
<content>
<<<<<<< SEARCH
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv # type: ignore
import psycopg2 # type: ignore
import numpy as np
import joblib # type: ignore
from tensorflow.keras.models import load_model # type: ignore
from flask import Flask, request, jsonify # type: ignore
from datetime import datetime, timedelta

load_dotenv()
app = Flask(__name__)

# Configure cache
CACHE_DURATION = timedelta(minutes=5)
prediction_cache = {}

# Load environment variables
API_KEY = os.getenv("WEATHER_API_KEY")
DB_PARAMS = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),

import os
import sys
import jwt  # type: ignore
from functools import wraps
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv # type: ignore
import psycopg2 # type: ignore
import numpy as np
import joblib # type: ignore
import h2o # type: ignore
from h2o.estimators import H2OGradientBoostingEstimator # type: ignore
from flask import Flask, request, jsonify, abort # type: ignore
from datetime import datetime, timedelta

load_dotenv()
app = Flask(__name__)

# Configure cache
CACHE_DURATION = timedelta(minutes=5)
prediction_cache = {}

# Load environment variables
API_KEY = os.getenv("WEATHERAPI_KEY")
DB_PARAMS = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}
JWT_SECRET = os.getenv("JWT_SECRET", "your_jwt_secret_key")  # Add a default for development

# Initialize H2O
h2o.init()
model_path = os.path.join(os.path.dirname(__file__), "h2o_automl_model", "GLM_1_AutoML_1_20250425_144833")
try:
    model = h2o.load_model(model_path)
except Exception as e:
    print(f"Error loading H2O model from {model_path}: {e}")
    model = None

def require_api_key(func):
    def wrapper(*args, **kwargs):
        key = request.headers.get('x-api-key') or request.args.get('api_key')
        if not key or key != API_KEY:
            abort(401, description="Unauthorized: API key is missing or invalid")
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

def require_jwt(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization', None)
        if not auth_header:
            abort(401, description="Unauthorized: Missing Authorization header")
        parts = auth_header.split()
        if parts[0].lower() != 'bearer' or len(parts) != 2:
            abort(401, description="Unauthorized: Invalid Authorization header format")
        token = parts[1]
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            # Optionally, you can add user info to request context here
        except jwt.ExpiredSignatureError:
            abort(401, description="Unauthorized: Token has expired")
        except jwt.InvalidTokenError:
            abort(401, description="Unauthorized: Invalid token")
        return func(*args, **kwargs)
    return wrapper

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
        return jsonify({'token': token})
    else:
        abort(401, description="Unauthorized: Invalid credentials")

# Define prediction endpoint using H2O model
@app.route('/predict', methods=['POST'])
@require_jwt
def predict():
    if model is None:
        return jsonify({'error': 'Model not loaded'}), 500
    data = request.get_json()
    # Convert input data to H2OFrame
    h2o_data = h2o.H2OFrame(data)
    # Make prediction
    prediction = model.predict(h2o_data)
    # Convert prediction to JSON serializable format
    pred_list = prediction.as_data_frame().values.flatten().tolist()
    return jsonify({'prediction': pred_list})

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
    app.run()

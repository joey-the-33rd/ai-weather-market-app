import json
import pytest
import sys
sys.path.insert(0, '..')
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app_server import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_predict_happy_path(client):
    data = [{
        "humidity_percent": 60,
        "wind_speed_kmh": 10,
        "pressure_hpa": 1013,
        "precipitation_mm": 0,
        "wind_direction_deg": 180,
        "uv_index": 5,
        "air_quality_index": 50,
        "cloud_cover_percent": 20,
        "visibility_km": 10,
        "dew_point_c": 15,
        "solar_radiation_w_m2": 200,
        "weather_condition": None
    }]
    response = client.post('/predict', json=data)
    if response.status_code != 200:
        print("Error response:", response.get_json())
    assert response.status_code == 200
    json_data = response.get_json()
    assert "prediction" in json_data
    assert isinstance(json_data["prediction"], (float, int))

def test_predict_invalid_input(client):
    data = "invalid data"
    response = client.post('/predict', json=data)
    assert response.status_code == 400 or response.status_code == 500

def test_predict_empty_input(client):
    data = []
    response = client.post('/predict', json=data)
    assert response.status_code == 400
    # No further assertions since response is error

def test_predict_missing_fields(client):
    data = [{}]
    response = client.post('/predict', json=data)
    assert response.status_code == 200 or response.status_code == 400

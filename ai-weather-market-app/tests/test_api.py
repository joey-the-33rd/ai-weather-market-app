import json
import pytest
import sys
sys.path.insert(0, '..')
from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_predict_happy_path(client):
    data = [{"temp": 25, "humidity": 60, "wind": 5}]
    response = client.post('/predict', json=data)
    assert response.status_code == 200
    json_data = response.get_json()
    assert "prediction" in json_data
    assert isinstance(json_data["prediction"], list)

def test_predict_invalid_input(client):
    data = "invalid data"
    response = client.post('/predict', json=data)
    assert response.status_code == 400 or response.status_code == 500

def test_predict_empty_input(client):
    data = []
    response = client.post('/predict', json=data)
    assert response.status_code == 200
    json_data = response.get_json()
    assert "prediction" in json_data

def test_predict_missing_fields(client):
    data = [{}]
    response = client.post('/predict', json=data)
    assert response.status_code == 200 or response.status_code == 400

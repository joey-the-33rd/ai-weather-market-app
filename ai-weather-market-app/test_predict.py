import requests

def test_predict():
    url = "http://localhost:5000/predict"
    payload = {
        "weather_condition": "Clear",
        "humidity_percent": 75,
        "wind_speed_kmh": 15,
        "pressure_hpa": 1013,
        "precipitation_mm": 0.5,
        "wind_direction_deg": 180,
        "uv_index": 3,
        "air_quality_index": 42,
        "cloud_cover_percent": 20,
        "visibility_km": 10,
        "dew_point_c": 12,
        "solar_radiation_w_m2": 200
    }

    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("Prediction:", response.json().get("prediction"))
    else:
        print("Error:", response.status_code, response.text)

if __name__ == "__main__":
    test_predict()

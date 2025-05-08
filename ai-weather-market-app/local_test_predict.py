import h2o
import os

def time_to_seconds(time_str):
    from datetime import datetime
    t = datetime.strptime(time_str, "%H:%M:%S")
    return t.hour * 3600 + t.minute * 60 + t.second

def local_test_predict():
    h2o.init()

    model_path = os.path.join(os.path.dirname(__file__), 'models', 'h2o_automl_model', 'GLM_1_AutoML_1_20250425_144833')
    model = h2o.load_model(model_path)

    data = {
        "weather_condition": ["Clear"],
        "humidity_percent": [75],
        "wind_speed_kmh": [15],
        "pressure_hpa": [1013],
        "precipitation_mm": [0.5],
        "wind_direction_deg": [180],
        "uv_index": [3],
        "air_quality_index": [42],
        "cloud_cover_percent": [20],
        "visibility_km": [10],
        "dew_point_c": [12],
        "solar_radiation_w_m2": [200]
    }

    hf = h2o.H2OFrame(data)

    pred = model.predict(hf)
    print(pred)

if __name__ == "__main__":
    local_test_predict()

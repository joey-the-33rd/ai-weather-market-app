"""Train and evaluate the Kenya one-hour-ahead weather model.

Historical data is downloaded from Open-Meteo. The latest 20% of each location's
timeline is held out chronologically to measure generalization.
"""
from __future__ import annotations
import argparse
from datetime import date, timedelta
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import requests
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error
from weather_model import FEATURE_COLUMNS

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
HOURLY_VARIABLES = [
    "temperature_2m", "relative_humidity_2m", "dew_point_2m", "precipitation",
    "pressure_msl", "cloud_cover", "wind_speed_10m", "wind_direction_10m",
    "shortwave_radiation",
]
LOCATIONS = [
    {"name": "Nairobi", "latitude": -1.2864, "longitude": 36.8172},
    {"name": "Mairo Inya", "latitude": -0.62, "longitude": 36.37},
    {"name": "Eldoret", "latitude": 0.5143, "longitude": 35.2698},
    {"name": "Kisumu", "latitude": -0.0917, "longitude": 34.7680},
    {"name": "Mombasa", "latitude": -4.0435, "longitude": 39.6682},
    {"name": "Lodwar", "latitude": 3.1190, "longitude": 35.5970},
]

def make_features(frame: pd.DataFrame, latitude: float, longitude: float) -> pd.DataFrame:
    stamp = pd.to_datetime(frame["time"])
    direction = np.deg2rad(frame["wind_direction_10m"].astype(float))
    features = pd.DataFrame({
        "temperature_c": frame["temperature_2m"],
        "humidity_percent": frame["relative_humidity_2m"],
        "dew_point_c": frame["dew_point_2m"],
        "precipitation_mm": frame["precipitation"],
        "pressure_hpa": frame["pressure_msl"],
        "cloud_cover_percent": frame["cloud_cover"],
        "wind_speed_kmh": frame["wind_speed_10m"],
        "wind_direction_sin": np.sin(direction), "wind_direction_cos": np.cos(direction),
        "solar_radiation_w_m2": frame["shortwave_radiation"],
        "latitude": latitude, "longitude": longitude,
        "hour_sin": np.sin(2 * np.pi * stamp.dt.hour / 24.0),
        "hour_cos": np.cos(2 * np.pi * stamp.dt.hour / 24.0),
        "day_of_year_sin": np.sin(2 * np.pi * stamp.dt.dayofyear / 365.25),
        "day_of_year_cos": np.cos(2 * np.pi * stamp.dt.dayofyear / 365.25),
    })
    return features[FEATURE_COLUMNS]

def fetch_location(location: dict, start_date: str, end_date: str) -> pd.DataFrame:
    params = {
        "latitude": location["latitude"], "longitude": location["longitude"],
        "start_date": start_date, "end_date": end_date,
        "hourly": ",".join(HOURLY_VARIABLES), "timezone": "Africa/Nairobi",
        "wind_speed_unit": "kmh", "precipitation_unit": "mm",
    }
    response = requests.get(ARCHIVE_URL, params=params, timeout=(10, 90))
    response.raise_for_status()
    payload = response.json()
    if "hourly" not in payload or not payload["hourly"].get("time"):
        raise RuntimeError(f"No historical hourly data returned for {location['name']}.")
    raw = pd.DataFrame(payload["hourly"])
    features = make_features(raw, location["latitude"], location["longitude"])
    features["target_temperature_c"] = raw["temperature_2m"].shift(-1)
    features["target_precipitation_mm"] = raw["precipitation"].shift(-1)
    features["timestamp"] = pd.to_datetime(raw["time"])
    features["location"] = location["name"]
    features = features.replace([np.inf, -np.inf], np.nan)
    return features.dropna(subset=FEATURE_COLUMNS + [
        "target_temperature_c", "target_precipitation_mm"
    ]).reset_index(drop=True)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-date", default=None, help="Historical start date YYYY-MM-DD (default: about 5 years)")
    parser.add_argument("--end-date", default=None, help="Historical end date YYYY-MM-DD (default: 7 days ago)")
    parser.add_argument("--output", default="weather_model.joblib", help="Output model artifact path")
    args = parser.parse_args()
    end = date.fromisoformat(args.end_date) if args.end_date else date.today() - timedelta(days=7)
    start = date.fromisoformat(args.start_date) if args.start_date else end - timedelta(days=5 * 365)
    if start >= end:
        raise ValueError("--start-date must be earlier than --end-date")

    frames = []
    for location in LOCATIONS:
        print(f"Downloading hourly weather for {location['name']}: {start} to {end}")
        frame = fetch_location(location, start.isoformat(), end.isoformat())
        cutoff = int(len(frame) * 0.8)
        if cutoff < 1000 or len(frame) - cutoff < 100:
            raise RuntimeError(f"Not enough usable historical rows for {location['name']}: {len(frame)}")
        frame["split"] = "train"
        frame.loc[cutoff:, "split"] = "test"
        # Avoid using a training label whose target timestamp is in the test window.
        frame.loc[cutoff - 1, "split"] = "discard"
        frames.append(frame)

    data = pd.concat(frames, ignore_index=True)
    train = data[data["split"] == "train"]
    test = data[data["split"] == "test"]
    x_train, x_test = train[FEATURE_COLUMNS], test[FEATURE_COLUMNS]
    medians = x_train.median(numeric_only=True).to_dict()
    x_train, x_test = x_train.fillna(medians), x_test.fillna(medians)
    y_temp_train, y_temp_test = train["target_temperature_c"], test["target_temperature_c"]
    y_rain_train, y_rain_test = train["target_precipitation_mm"], test["target_precipitation_mm"]

    temp_model = HistGradientBoostingRegressor(
        max_iter=180, learning_rate=0.07, max_leaf_nodes=24, l2_regularization=1.0, random_state=42
    )
    rain_model = HistGradientBoostingRegressor(
        max_iter=180, learning_rate=0.07, max_leaf_nodes=24, l2_regularization=1.0, random_state=43
    )
    print(f"Training on {len(train):,} rows; evaluating on {len(test):,} held-out rows.")
    temp_model.fit(x_train, y_temp_train)
    rain_model.fit(x_train, y_rain_train)
    temp_pred = temp_model.predict(x_test)
    rain_pred = np.maximum(0.0, rain_model.predict(x_test))
    metrics = {
        "temperature_mae_c": round(float(mean_absolute_error(y_temp_test, temp_pred)), 4),
        "temperature_persistence_mae_c": round(float(mean_absolute_error(y_temp_test, test["temperature_c"])), 4),
        "precipitation_mae_mm": round(float(mean_absolute_error(y_rain_test, rain_pred)), 4),
        "precipitation_persistence_mae_mm": round(float(mean_absolute_error(y_rain_test, test["precipitation_mm"])), 4),
        "train_rows": int(len(train)), "test_rows": int(len(test)),
    }
    bundle = {
        "model_name": "Kenya One-Hour Weather Forecast", "model_version": 1,
        "feature_columns": FEATURE_COLUMNS, "feature_medians": medians,
        "temperature_model": temp_model, "precipitation_model": rain_model,
        "metrics": metrics, "trained_from": start.isoformat(), "trained_through": end.isoformat(),
        "locations": [item["name"] for item in LOCATIONS],
        "data_source": "Open-Meteo Historical Weather API (ERA5/ERA5-Land reanalysis)",
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, output)
    print(f"\nSaved model artifact: {output.resolve()}")
    print("Held-out metrics (lower MAE is better):")
    for key, value in metrics.items():
        print(f"  {key}: {value}")
    if metrics["temperature_mae_c"] >= metrics["temperature_persistence_mae_c"]:
        print("WARNING: temperature model did not beat the persistence baseline; tune before relying on it.")
    if metrics["precipitation_mae_mm"] >= metrics["precipitation_persistence_mae_mm"]:
        print("WARNING: precipitation model did not beat the persistence baseline; tune before relying on it.")
    print("Holdout scores are not a guarantee of future real-world forecast accuracy.")

if __name__ == "__main__":
    main()

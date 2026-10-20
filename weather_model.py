"""One-hour-ahead weather forecasting utilities."""
from __future__ import annotations
from typing import Any
import joblib
import numpy as np
import pandas as pd

FEATURE_COLUMNS = [
    "temperature_c", "humidity_percent", "dew_point_c", "precipitation_mm",
    "pressure_hpa", "cloud_cover_percent", "wind_speed_kmh",
    "wind_direction_sin", "wind_direction_cos", "solar_radiation_w_m2",
    "latitude", "longitude", "hour_sin", "hour_cos",
    "day_of_year_sin", "day_of_year_cos",
]

def _cyclic_features(timestamp: Any) -> dict[str, float]:
    stamp = pd.Timestamp(timestamp)
    hour_angle = 2 * np.pi * stamp.hour / 24.0
    year_angle = 2 * np.pi * stamp.dayofyear / 365.25
    return {
        "hour_sin": float(np.sin(hour_angle)), "hour_cos": float(np.cos(hour_angle)),
        "day_of_year_sin": float(np.sin(year_angle)), "day_of_year_cos": float(np.cos(year_angle)),
    }

def provider_hour_to_features(hour: dict, latitude: float, longitude: float) -> dict[str, float]:
    """Map a WeatherAPI.com hourly forecast record to the training feature schema."""
    stamp = hour.get("time")
    if not stamp:
        raise ValueError("Weather record is missing its timestamp.")
    direction = hour.get("wind_degree")
    direction_radians = np.deg2rad(float(direction)) if direction is not None else np.nan
    features = {
        "temperature_c": hour.get("temp_c"), "humidity_percent": hour.get("humidity"),
        "dew_point_c": hour.get("dewpoint_c"), "precipitation_mm": hour.get("precip_mm"),
        "pressure_hpa": hour.get("pressure_mb"), "cloud_cover_percent": hour.get("cloud"),
        "wind_speed_kmh": hour.get("wind_kph"),
        "wind_direction_sin": float(np.sin(direction_radians)) if np.isfinite(direction_radians) else np.nan,
        "wind_direction_cos": float(np.cos(direction_radians)) if np.isfinite(direction_radians) else np.nan,
        "solar_radiation_w_m2": hour.get("short_rad"), "latitude": latitude, "longitude": longitude,
    }
    features.update(_cyclic_features(stamp))
    return features

def predict_next_hour(bundle: dict, features: dict[str, float]) -> dict[str, float]:
    frame = pd.DataFrame([features], columns=FEATURE_COLUMNS)
    frame = frame.fillna(bundle.get("feature_medians", {}))
    if frame.isna().any().any():
        raise ValueError("Some model features are missing and have no training median.")
    temperature = float(bundle["temperature_model"].predict(frame)[0])
    precipitation = max(0.0, float(bundle["precipitation_model"].predict(frame)[0]))
    return {"temperature_c": round(temperature, 2), "precipitation_mm": round(precipitation, 2)}

def load_model_bundle(path: str) -> dict:
    bundle = joblib.load(path)
    required = {"temperature_model", "precipitation_model", "feature_medians", "metrics"}
    if not isinstance(bundle, dict) or not required.issubset(bundle):
        raise ValueError("The weather model artifact has an invalid format.")
    if bundle.get("feature_columns") != FEATURE_COLUMNS:
        raise ValueError("The weather model feature schema does not match this API.")
    return bundle

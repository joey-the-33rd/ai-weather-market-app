#!/bin/bash

# Get JWT token from login endpoint
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:5050/login -H "Content-Type: application/json" -d '{"username":"admin","password":"password"}')
TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.token')

echo "✅ 🔐 Received JWT token: $TOKEN"

# Use the token to call the protected /predict endpoint with sample data
curl -s -X POST http://localhost:5050/predict \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
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
    "weather_condition": "Sunny"
  }'
echo

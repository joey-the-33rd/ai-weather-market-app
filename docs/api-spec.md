# API Specification for AI Weather Market App

## Overview

This document details the API endpoints available in the AI Weather Market App, including their request formats, response formats, and possible error responses.

---

## 1. GET /

- **URL:** `/`
- **Method:** GET
- **Description:** Returns a welcome message for the API.

### Response

- **Status Code:** 200 OK
- **Content-Type:** text/plain

```text
Welcome to the AI Weather Market App API. Use the /predict endpoint to get weather predictions.
```

---

## 2. POST /predict

- **URL:** `/predict`
- **Method:** POST
- **Description:** Accepts live weather data as a JSON payload and returns an AI model prediction based on the input data.

### Request Body

Content-Type: application/json

The JSON payload should include the following fields:

| Field                 | Type    | Required | Description                                  |
|-----------------------|---------|----------|----------------------------------------------|
| humidity_percent      | number  | Yes      | Humidity percentage                          |
| wind_speed_kmh        | number  | Yes      | Wind speed in kilometers per hour            |
| pressure_hpa          | number  | Yes      | Atmospheric pressure in hPa                   |
| precipitation_mm      | number  | Yes      | Precipitation in millimeters                  |
| wind_direction_deg    | number  | Yes      | Wind direction in degrees                      |
| uv_index              | number  | Yes      | UV index                                      |
| air_quality_index     | number  | Yes      | Air quality index                             |
| cloud_cover_percent   | number  | Yes      | Cloud cover percentage                         |
| visibility_km         | number  | Yes      | Visibility in kilometers                       |
| dew_point_c           | number  | Yes      | Dew point in Celsius                           |
| solar_radiation_w_m2  | number  | Yes      | Solar radiation in watts per square meter     |
| weather_condition     | string  | No       | Weather condition (categorical, optional)    |

The `weather_condition` field can be one of the following values (case-sensitive):

- Sunny
- Clear
- Partly cloudy
- Cloudy
- Overcast
- Mist
- Patchy rain possible
- Patchy snow possible
- Patchy sleet possible
- Patchy freezing drizzle possible
- Thundery outbreaks possible
- Blowing snow
- Blizzard
- Fog
- Freezing fog
- Patchy light drizzle
- Light drizzle
- Freezing drizzle
- Heavy freezing drizzle
- Patchy light rain
- Light rain
- Moderate rain at times
- Moderate rain
- Heavy rain at times
- Heavy rain
- Light freezing rain
- Moderate or heavy freezing rain
- Light sleet
- Moderate or heavy sleet
- Patchy light snow
- Light snow
- Patchy moderate snow
- Moderate snow
- Patchy heavy snow
- Heavy snow
- Ice pellets
- Light rain shower
- Moderate or heavy rain shower
- Torrential rain shower
- Light sleet showers
- Moderate or heavy sleet showers
- Light snow showers
- Moderate or heavy snow showers
- Light showers of ice pellets
- Moderate or heavy showers of ice pellets
- Patchy light rain with thunder
- Moderate or heavy rain with thunder
- Patchy light snow with thunder
- Moderate or heavy snow with thunder

### Response

- **Status Code:** 200 OK
- **Content-Type:** application/json

```json
{
  "prediction": <number>
}
```

Where `<number>` is the predicted value from the AI model.

### Error Responses

- **400 Bad Request**

```json
{
  "error": "No input data provided"
}
```

or

```json
{
  "error": "Missing required field: <field_name>"
}
```

- **500 Internal Server Error**

```json
{
  "error": "<error_message>"
}
```

---

## 3. GET /api/weather

- **URL:** `/api/weather`
- **Method:** GET
- **Description:** Returns mock weather data for a specified city.

### Query Parameters

| Parameter | Type   | Required | Description          |
|-----------|--------|----------|----------------------|
| city      | string | Yes      | Name of the city     |

### Response

- **Status Code:** 200 OK
- **Content-Type:** application/json

```json
{
  "temperature": 25,
  "humidity": 60,
  "weather": "Sunny",
  "city": "<city_name>"
}
```

Where `<city_name>` is the city specified in the query parameter.

### Error Responses

- **400 Bad Request**

```json
{
  "error": "City parameter is required"
}
```

---

# End of API Specification

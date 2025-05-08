#!/Users/melchizedekvii/Documents/GitHub/ai-weather-market-app/ai-weather-market-app/aiwma_env/bin/python3
import psycopg2  # type: ignore
from datetime import datetime, timedelta
import pytz  # type: ignore
from dotenv import load_dotenv # type: ignore
import os
import random
import numpy as np  # type: ignore
import requests
import time

# Load environment variables from .env file
load_dotenv()

# Fetch credentials securely
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
WEATHERAPI_KEY = os.getenv("WEATHERAPI_KEY")

# Function to fetch historical weather data from weatherapi.com
def fetch_historical_weather(date, city="Nairobi"):
    url = f"http://api.weatherapi.com/v1/history.json"
    params = {
        "key": WEATHERAPI_KEY,
        "q": city,
        "dt": date.strftime("%Y-%m-%d")
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.RequestException as e:
        print(f"Error fetching data for {date}: {e}")
        return None

# Parse weatherapi.com response to match weather_data table schema
def parse_weather_data(api_data):
    if not api_data or "forecast" not in api_data:
        return None
    forecast_day = api_data["forecast"]["forecastday"][0]
    day = forecast_day["day"]
    astro = forecast_day["astro"]
    hour = forecast_day["hour"][12]  # Approx midday data

    record = {
        "city": api_data["location"]["name"],
        "country": api_data["location"]["country"][:2],  # Take first 2 chars as country code
        "latitude": api_data["location"]["lat"],
        "longitude": api_data["location"]["lon"],
        "recorded_at": datetime.strptime(forecast_day["date"], "%Y-%m-%d"),
        "temperature_c": day["avgtemp_c"],
        "humidity_percent": day["avghumidity"],
        "wind_speed_kmh": day["maxwind_kph"],
        "pressure_hpa": hour.get("pressure_mb", None),
        "precipitation_mm": day["totalprecip_mm"],
        "wind_direction_deg": hour.get("wind_degree", None),
        "uv_index": day.get("uv", None),
        "air_quality_index": None,  # Not provided by weatherapi.com free tier
        "weather_condition": day["condition"]["text"],
        "cloud_cover_percent": hour.get("cloud", None),
        "visibility_km": hour.get("vis_km", None),
        "dew_point_c": None,  # Not provided
        "solar_radiation_w_m2": None,  # Not provided
        "sunrise_time": datetime.strptime(astro["sunrise"], "%I:%M %p").time(),
        "sunset_time": datetime.strptime(astro["sunset"], "%I:%M %p").time()
    }
    return record

# Connect and insert data
def insert_weather_data(records):
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()

        # Create weather_data table if it doesn't exist
        create_table_query = """
        CREATE TABLE IF NOT EXISTS weather_data (
            id SERIAL PRIMARY KEY,
            city VARCHAR(100),
            country VARCHAR(2),
            latitude DECIMAL(9,6),
            longitude DECIMAL(9,6),
            recorded_at TIMESTAMP,
            temperature_c FLOAT,
            humidity_percent FLOAT,
            pressure_hpa FLOAT,
            wind_speed_kmh FLOAT,
            wind_direction_deg FLOAT,
            precipitation_mm FLOAT,
            uv_index FLOAT,
            air_quality_index FLOAT,
            weather_condition VARCHAR(50),
            cloud_cover_percent FLOAT,
            visibility_km FLOAT,
            dew_point_c FLOAT,
            solar_radiation_w_m2 FLOAT,
            sunrise_time TIME,
            sunset_time TIME
        )
        """
        cursor.execute(create_table_query)
        conn.commit()

        insert_query = """
        INSERT INTO weather_data (
            city, country, latitude, longitude, recorded_at,
            temperature_c, humidity_percent, pressure_hpa, wind_speed_kmh,
            wind_direction_deg, precipitation_mm, uv_index, air_quality_index,
            weather_condition, cloud_cover_percent, visibility_km, dew_point_c,
            solar_radiation_w_m2, sunrise_time, sunset_time
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        for record in records:
            cursor.execute(insert_query, (
                record["city"],
                record["country"],
                record["latitude"],
                record["longitude"],
                record["recorded_at"],
                record["temperature_c"],
                record["humidity_percent"],
                record["pressure_hpa"],
                record["wind_speed_kmh"],
                record["wind_direction_deg"],
                record["precipitation_mm"],
                record["uv_index"],
                record["air_quality_index"],
                record["weather_condition"],
                record["cloud_cover_percent"],
                record["visibility_km"],
                record["dew_point_c"],
                record["solar_radiation_w_m2"],
                record["sunrise_time"],
                record["sunset_time"]
            ))

        conn.commit()
        print(f"✅ {len(records)} weather records inserted successfully.")

    except Exception as e:
        print("❌ Error:", e)

    finally:
        if 'conn' in locals() and conn:
            cursor.close()
            conn.close()

# New function to fetch and insert latest weather data every interval seconds
def fetch_and_insert_realtime_weather(city="Nairobi", interval=300):
    while True:
        url = f"http://api.weatherapi.com/v1/current.json"
        params = {
            "key": WEATHERAPI_KEY,
            "q": city
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            record = {
                "city": data["location"]["name"],
                "country": data["location"]["country"][:2],
                "latitude": data["location"]["lat"],
                "longitude": data["location"]["lon"],
                "recorded_at": datetime.strptime(data["location"]["localtime"], "%Y-%m-%d %H:%M"),
                "temperature_c": data["current"]["temp_c"],
                "humidity_percent": data["current"]["humidity"],
                "wind_speed_kmh": data["current"]["wind_kph"],
                "pressure_hpa": data["current"]["pressure_mb"],
                "precipitation_mm": data["current"]["precip_mm"],
                "wind_direction_deg": data["current"]["wind_degree"],
                "uv_index": data["current"].get("uv", None),
                "air_quality_index": None,
                "weather_condition": data["current"]["condition"]["text"],
                "cloud_cover_percent": data["current"].get("cloud", None),
                "visibility_km": data["current"].get("vis_km", None),
                "dew_point_c": None,
                "solar_radiation_w_m2": None,
                "sunrise_time": None,
                "sunset_time": None
            }
            insert_weather_data([record])
            print(f"✅ Inserted real-time weather data for {city} at {record['recorded_at']}")
        except Exception as e:
            print(f"❌ Error fetching real-time data: {e}")

        time.sleep(interval)

# Main function to fetch and insert historical data with rate limiting
def main():
    start_date = datetime(2023, 1, 1)
    end_date = datetime.now()
    delta = timedelta(days=1)
    city = "Nairobi"
    records_to_insert = []

    current_date = start_date
    while current_date <= end_date:
        api_data = fetch_historical_weather(current_date, city)
        record = parse_weather_data(api_data)
        if record:
            records_to_insert.append(record)

        # Insert in batches of 10 to reduce DB commits
        if len(records_to_insert) >= 10:
            insert_weather_data(records_to_insert)
            records_to_insert = []

        current_date += delta

        # Rate limiting: sleep 1 second between API calls to avoid hitting limits
        time.sleep(1)

    # Insert any remaining records
    if records_to_insert:
        insert_weather_data(records_to_insert)

if __name__ == "__main__":
    main()

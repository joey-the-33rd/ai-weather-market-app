import psycopg2  # type: ignore
from datetime import datetime, timedelta
import pytz  # type: ignore
from dotenv import load_dotenv # type: ignore
import os
import random
import numpy as np  # type: ignore

# Load environment variables from .env file
load_dotenv()

# Fetch credentials securely
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# Generate realistic weather data for 100 records
def generate_weather_data(num_records=100):
    base_time = datetime.now(pytz.utc)
    records = []
    
    for i in range(num_records):
        # Generate realistic variations
        time_offset = timedelta(hours=i)
        temp_variation = np.sin(i/10) * 5  # Daily temperature cycle
        humidity_variation = np.cos(i/12) * 15  # Daily humidity cycle
        
        record = {
            "city": "Nairobi",
            "country": "KE",
            "latitude": -1.286389 + random.uniform(-0.01, 0.01),
            "longitude": 36.817223 + random.uniform(-0.01, 0.01),
            "recorded_at": base_time - time_offset,
            "temperature_c": 24.76 + temp_variation + random.uniform(-2, 2),
            "humidity_percent": max(40, min(90, 62.50 + humidity_variation + random.uniform(-10, 10))),
            "wind_speed_kmh": max(0, 13.20 + random.uniform(-5, 10)),
            "pressure_hpa": 1012.50 + random.uniform(-5, 5),
            "precipitation_mm": max(0, random.uniform(0, 5) if random.random() > 0.7 else 0),
            "wind_direction_deg": random.uniform(0, 360),
            "uv_index": random.uniform(0, 11),
            "air_quality_index": random.uniform(0, 500),
            "weather_condition": random.choice(["Clear", "Partly cloudy", "Cloudy", "Light rain", "Foggy"]),
            "cloud_cover_percent": random.uniform(0, 100),
            "visibility_km": random.uniform(1, 20),
            "dew_point_c": random.uniform(10, 20),
            "solar_radiation_w_m2": random.uniform(0, 1000),
            "sunrise_time": (base_time - timedelta(hours=6)).time(),
            "sunset_time": (base_time + timedelta(hours=6)).time()
        }
        records.append(record)
    
    return records

# Connect and insert data
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

    # Insert new records
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

    weather_records = generate_weather_data(200)  # Generate 200 records
    for record in weather_records:
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
    print(f"✅ {len(weather_records)} weather records inserted successfully.")

except Exception as e:
    print("❌ Error:", e)

finally:
    if 'conn' in locals() and conn:
        cursor.close()
        conn.close()

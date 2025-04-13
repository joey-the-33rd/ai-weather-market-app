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
            "location": "Nairobi, Kenya",
            "latitude": -1.286389 + random.uniform(-0.01, 0.01),
            "longitude": 36.817223 + random.uniform(-0.01, 0.01),
            "recorded_at": base_time - time_offset,
            "temperature_c": 24.76 + temp_variation + random.uniform(-2, 2),
            "humidity_percent": max(40, min(90, 62.50 + humidity_variation + random.uniform(-10, 10))),
            "wind_speed_kmh": max(0, 13.20 + random.uniform(-5, 10)),
            "pressure_hpa": 1012.50 + random.uniform(-5, 5),
            "precipitation_mm": max(0, random.uniform(0, 5) if random.random() > 0.7 else 0),
            "city": "Nairobi",
            "weather_condition": random.choice(["Clear", "Partly cloudy", "Cloudy", "Light rain", "Foggy"])
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
        location TEXT,
        latitude FLOAT,
        longitude FLOAT,
        recorded_at TIMESTAMP WITH TIME ZONE,
        temperature_c FLOAT,
        humidity_percent FLOAT,
        wind_speed_kmh FLOAT,
        pressure_hpa FLOAT,
        precipitation_mm FLOAT,
        city TEXT,
        weather_condition TEXT
    )
    """
    cursor.execute(create_table_query)
    conn.commit()

    # Insert new records
    insert_query = """
    INSERT INTO weather_data (
        location, latitude, longitude, recorded_at,
        temperature_c, humidity_percent, wind_speed_kmh,
        pressure_hpa, precipitation_mm, city, weather_condition
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    weather_records = generate_weather_data(200)  # Generate 200 records
    for record in weather_records:
        cursor.execute(insert_query, (
            record["location"],
            record["latitude"],
            record["longitude"],
            record["recorded_at"],
            record["temperature_c"],
            record["humidity_percent"],
            record["wind_speed_kmh"],
            record["pressure_hpa"],
            record["precipitation_mm"],
            record["city"],
            record["weather_condition"]
        ))

    conn.commit()
    print(f"✅ {len(weather_records)} weather records inserted successfully.")

except Exception as e:
    print("❌ Error:", e)

finally:
    if 'conn' in locals() and conn:
        cursor.close()
        conn.close()

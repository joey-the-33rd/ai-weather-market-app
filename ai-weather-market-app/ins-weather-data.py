import psycopg2 # type: ignore
from datetime import datetime

# Replace with your actual DB credentials
DB_NAME = "weather_db"
DB_USER = "postgres"
DB_PASSWORD = "yourpassword"
DB_HOST = "localhost"
DB_PORT = "5432"

# Sample weather data
weather_data = {
    "location": "Nairobi, Kenya",
    "latitude": -1.286389,
    "longitude": 36.817223,
    "recorded_at": datetime.utcnow(),
    "temperature_c": 24.76,
    "humidity_percent": 62.50,
    "wind_speed_kmh": 13.20,
    "pressure_hpa": 1012.50,
    "precipitation_mm": 1.80,
    "city": "Nairobi",
    "weather_condition": "Partly cloudy"
}

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

    insert_query = """
    INSERT INTO weather_data (
        location, latitude, longitude, recorded_at,
        temperature_c, humidity_percent, wind_speed_kmh,
        pressure_hpa, precipitation_mm, city, weather_condition
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    cursor.execute(insert_query, (
        weather_data["location"],
        weather_data["latitude"],
        weather_data["longitude"],
        weather_data["recorded_at"],
        weather_data["temperature_c"],
        weather_data["humidity_percent"],
        weather_data["wind_speed_kmh"],
        weather_data["pressure_hpa"],
        weather_data["precipitation_mm"],
        weather_data["city"],
        weather_data["weather_condition"]
    ))

    conn.commit()
    print("✅ Weather data inserted successfully.")

except Exception as e:
    print("❌ Error inserting weather data:", e)

finally:
    if conn:
        cursor.close()
        conn.close()

#!/Users/melchizedekvii/Documents/GitHub/ai-weather-market-app/ai-weather-market-app/aiwma_env/bin/python3
import psycopg2  
from datetime import datetime, timedelta
import pytz  
from dotenv import load_dotenv
import os
import random
import numpy as np  
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

if not WEATHERAPI_KEY:
    print("❌ ERROR: WEATHERAPI_KEY is not set. Please set the WEATHERAPI_KEY environment variable or add it to your .env file.")
    import sys
    sys.exit(1)

# Function to fetch historical weather data from weatherapi.com
def fetch_historical_weather(date, city="Nairobi"):
    """
    Fetch historical weather data for a given date and city from weatherapi.com.

    Args:
        date (datetime): The date for which to fetch the historical weather data.
        city (str, optional): The name of the city for which to fetch the data. Defaults to "Nairobi".

    Returns:
        dict: A dictionary containing the weather data if the request is successful, or None if there is an error.
    """

    url = f"https://api.weatherapi.com/v1/history.json"
    params = {
        "key": WEATHERAPI_KEY,
        "q": city,
        "dt": date.strftime("%Y-%m-%d")
    }
    masked_params = params.copy()
    if "key" in masked_params:
        masked_params["key"] = "****"
    print(f"DEBUG: Requesting URL: {url} with params: {masked_params}")
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.RequestException as e:
        if e.response is not None:
            print(f"Error fetching data for {date}: {e} - Response content: {e.response.text}")
        else:
            print(f"Error fetching data for {date}: {e}")
        return None

# Parse weatherapi.com response to match weather_data table schema
def parse_weather_data(api_data):
    """
    Parse a weatherapi.com response into a dict matching the weather_data table schema.

    Args:
        api_data (dict): The JSON response from weatherapi.com.

    Returns:
        dict: A dictionary containing the parsed weather data, or None if the request is unsuccessful.
    """

    if not api_data or "forecast" not in api_data or "forecastday" not in api_data["forecast"] or len(api_data["forecast"]["forecastday"]) == 0:
        return None
    day_data = api_data["forecast"]["forecastday"][0]["day"]
    astro_data = api_data["forecast"]["forecastday"][0].get("astro", {})

    record = {
        "city": api_data.get("location", {}).get("name", "Unknown"),
        "country": api_data.get("location", {}).get("country", None),
        "latitude": api_data.get("location", {}).get("lat", None),
        "longitude": api_data.get("location", {}).get("lon", None),
-        "recorded_at": datetime.strptime(api_data.get("location", {}).get("localtime", date.strftime("%Y-%m-%d")), "%Y-%m-%d %H:%M"),
+        "recorded_at": datetime.strptime(api_data.get("location", {}).get("localtime", ""), "%Y-%m-%d %H:%M") if api_data.get("location", {}).get("localtime") else None,
        "temperature_c": day_data.get("avgtemp_c", None),
        "humidity_percent": day_data.get("avghumidity", None),
        "wind_speed_kmh": day_data.get("maxwind_kph", None),
        "pressure_hpa": day_data.get("pressure_mb", None),
        "precipitation_mm": day_data.get("totalprecip_mm", None),
        "wind_direction_deg": None,
        "uv_index": day_data.get("uv", None),
        "air_quality_index": None,
        "weather_condition": day_data.get("condition", {}).get("text", None),
        "cloud_cover_percent": None,
        "visibility_km": None,
        "dew_point_c": None,
        "solar_radiation_w_m2": None,
        "sunrise_time": datetime.strptime(astro_data.get("sunrise", "06:00 AM"), "%I:%M %p").time() if "sunrise" in astro_data else None,
        "sunset_time": datetime.strptime(astro_data.get("sunset", "06:00 PM"), "%I:%M %p").time() if "sunset" in astro_data else None
    }
    return record

# Connect and insert data
def insert_weather_data(records):
    """
    Insert weather data records into the weather_data table.

    Args:
        records (list[dict]): A list of dictionaries containing the weather data records to be inserted.

    Returns:
        None

    Raises:
        Exception: If an error occurs while connecting to the database, creating the table, or inserting the records.

    Notes:
        - If the weather_data table does not exist, it will be created.
        - The function will commit the records to the database if the insertion is successful.
        - If an error occurs, the function will not commit the records and will close the database connection.
    """
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
    """
    Continuously fetches and inserts real-time weather data for a specified city at regular intervals.

    Args:
        city (str): The name of the city for which to fetch the weather data. Defaults to "Nairobi".
        interval (int): The time interval in seconds between each API call. Defaults to 300 seconds (5 minutes).

    The function retrieves current weather data from weatherapi.com and inserts it into the weather_data table.
    The insertion is performed repeatedly at the specified interval. The function handles any exceptions that
    occur during data fetching and logs errors without stopping execution.
    """

    while True:
        url = f"https://api.weatherapi.com/v1/current.json"
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
    """
    Main function to fetch and insert historical weather data from weatherapi.com.

    Fetches historical data from 2023-01-01 to the current date for Nairobi, and inserts it into the weather_data table.

    Rate limited to 1 API call per second to avoid hitting the free tier limit of 50 requests per day.

    Inserts data in batches of 10 to reduce the number of database commits.

    :return: None
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
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

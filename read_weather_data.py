import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

def read_weather_data(limit=10):
    """
    Retrieves the last 'limit' number of records from the weather_data table
    and prints the records in a formatted manner.

    Parameters:
        limit (int): The number of records to retrieve (default is 10)

    Returns:
        None
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
        query = f"SELECT id, city, country, recorded_at, temperature_c, humidity_percent, weather_condition FROM weather_data ORDER BY recorded_at DESC LIMIT {limit};"
        cursor.execute(query)
        rows = cursor.fetchall()
        print(f"Last {limit} weather data records:")
        for row in rows:
            print(f"ID: {row[0]}, City: {row[1]}, Country: {row[2]}, Date: {row[3]}, Temp (C): {row[4]}, Humidity (%): {row[5]}, Condition: {row[6]}")
    except Exception as e:
        print("Error reading weather data:", e)
    finally:
        if 'conn' in locals() and conn:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    read_weather_data()

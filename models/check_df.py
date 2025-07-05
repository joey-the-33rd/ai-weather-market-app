import pandas as pd # type: ignore
import psycopg2 # type: ignore
from dotenv import load_dotenv # type: ignore
import os

# Load the environment variables from the .env file
load_dotenv()

# Define the database connection parameters from the environment variables
host = os.getenv('DB_HOST')
database = os.getenv('DB_NAME')
username = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')

# Establish a connection to the database
conn = psycopg2.connect(
    host=host,
    database=database,
    user=username,
    password=password
)

# Load the data from the PostgreSQL database
query = """
    SELECT 
        recorded_at,
        temperature_c,
        humidity_percent,
        wind_speed_kmh,
        pressure_hpa,
        precipitation_mm
    FROM weather.weather_data
    WHERE temperature_c IS NOT NULL
    ORDER BY recorded_at;
"""
df = pd.read_sql(query, conn)

# Check if the DataFrame is empty
if df.shape[0] > 0:
    print("DataFrame is not empty")
    print(df.head())
else:
    print("Error: DataFrame is empty")

# Close the database connection
conn.close()
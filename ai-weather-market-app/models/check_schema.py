import psycopg2 # type: ignore
import pandas as pd # type: ignore
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

# Get the schema and table names
schemas = pd.read_sql("SELECT schema_name FROM information_schema.schemata", conn)
tables = pd.read_sql("SELECT table_name FROM information_schema.tables WHERE table_schema = 'weather'", conn)
print(schemas)
print(tables)

# Close the database connection
conn.close()
import os
import sys
import psycopg2
import traceback
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Required environment variables
required_env_vars = ["DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD"]

# Fetch environment variables
db_host_raw = os.getenv("DB_HOST")
db_host = db_host_raw.split('#')[0].strip() if db_host_raw else None
db_port_raw = os.getenv("DB_PORT")
db_port = db_port_raw.split('#')[0].strip() if db_port_raw else None
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")

# Validate environment variables
missing_vars = [var for var, val in [("DB_HOST", db_host), ("DB_PORT", db_port), ("DB_NAME", db_name), ("DB_USER", db_user), ("DB_PASSWORD", db_password)] if not val]
if missing_vars:
    print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
    sys.exit(1)

assert db_port is not None, "DB_PORT environment variable is required"

# Fetch credentials from environment with proper types
db_config = {
    'host': str(db_host),
    'port': int(db_port),
    'dbname': str(db_name),
    'user': str(db_user),
    'password': str(db_password)
}

# Default output file
default_output_file = 'weather_data.csv'

# SQL export query
export_sql = f"""
COPY (
    SELECT * FROM weather_data
) TO STDOUT WITH CSV HEADER
"""

def export_weather_data(output_file=default_output_file):
    """
    Exports the weather data from the database to a CSV file.

    If the output file path is not provided, it will default to
    'weather_data.csv'.

    If an error occurs during export, it will be printed to the
    console and this function will return None.

    :param output_file: The path to write the exported CSV file to.
                        Defaults to 'weather_data.csv'.
    :type output_file: str
    :return: None
    :rtype: None
    """
    try:
        # Connect to the database
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()

        with open(output_file, 'w') as f:
            cur.copy_expert(export_sql, f)

        print(f"✅ Data exported successfully to {output_file}")

    except Exception as e:
        print(f"❌ Error during export: {e}")
        traceback.print_exc()
    finally:
        try:
            if cur:
                cur.close()
            if conn:
                conn.close()
        except Exception:
            pass

if __name__ == "__main__":
    # Allow output file path as command line argument
    output_file = sys.argv[1] if len(sys.argv) > 1 else default_output_file
    export_weather_data(output_file)

import os
import psycopg2 # type: ignore
import pandas as pd # type: ignore
from dotenv import load_dotenv # type: ignore
import h2o # type: ignore
from h2o.automl import H2OAutoML # type: ignore

# Load environment variables
load_dotenv()

# Secure DB credentials
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

# Connect to the database
try:
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    print("✅ Connected to PostgreSQL.")
except Exception as e:
    print("❌ Connection error:", e)
    exit()

# Query historical weather data with all relevant columns
query = """
SELECT 
    temperature_c,
    humidity_percent,
    wind_speed_kmh,
    pressure_hpa,
    precipitation_mm,
    wind_direction_deg,
    uv_index,
    air_quality_index,
    weather_condition,
    cloud_cover_percent,
    visibility_km,
    dew_point_c,
    solar_radiation_w_m2,
    sunrise_time,
    sunset_time
FROM weather_data
WHERE temperature_c IS NOT NULL
ORDER BY recorded_at;
"""

df = pd.read_sql(query, conn)
print(f"[INFO] Retrieved {len(df)} records from database")

# Handle missing values
df.dropna(inplace=True)
print(f"[INFO] After dropping nulls: {len(df)} records remain")

# Convert categorical weather_condition to factor for H2O
df['weather_condition'] = df['weather_condition'].astype('category')

# Initialize H2O
h2o.init()

# Convert pandas DataFrame to H2O Frame
hf = h2o.H2OFrame(df)

# Set target and features
y = "temperature_c"
X = hf.columns
X.remove(y)

# Run H2O AutoML for regression
aml = H2OAutoML(max_models=20, seed=42, max_runtime_secs=3600)
aml.train(x=X, y=y, training_frame=hf)

# View the AutoML Leaderboard
lb = aml.leaderboard
print(lb.head(rows=lb.nrows))

# Save the best model
model_path = h2o.save_model(model=aml.leader, path=os.path.join(os.path.dirname(__file__), "h2o_automl_model"), force=True)
print(f"[INFO] Best AutoML model saved to: {model_path}")

# Shutdown H2O cluster (optional)
# h2o.shutdown(prompt=False)

# Instructions:
# 1. Install H2O: pip install -f http://h2o-release.s3.amazonaws.com/h2o/latest_stable_Py.html h2o
# 2. Run this script to perform AutoML training and save the best model.
